import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import stripe

from .models import Item, Order, OrderItem
from .utils import (
    get_order_from_session,
    create_order_and_save_to_session,
    build_line_items,
    apply_discount_to_session,
    apply_tax_to_line_items
)


def item_page(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'items/item.html', {
        "item": item,
        "stripe_pk": settings.STRIPE_PUBLISHABLE_KEY,
    })


@require_POST
def buy_item(request: HttpRequest, item_id: int) -> JsonResponse:
    item = get_object_or_404(Item, id=item_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': item.price,
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                },
                'quantity': 1,
            }],
            success_url=request.build_absolute_uri('/success.html'),
            cancel_url=request.build_absolute_uri('/cancel.html'),
        )
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_POST
def buy_order(request: HttpRequest, order_id: int) -> JsonResponse:
    order = get_object_or_404(Order, id=order_id)
    
    if not order.order_items.exists():
        return JsonResponse({"error": "Cart is empty"}, status=400)
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    line_items = build_line_items(order)
    
    session_params = {
        'payment_method_types': ['card'],
        'line_items': line_items,
        'mode': 'payment',
        'success_url': request.build_absolute_uri('/success.html'),
        'cancel_url': request.build_absolute_uri('/cancel.html'),
        'metadata': {"order_id": str(order.id)},
    }
    
    apply_discount_to_session(order, session_params)
    apply_tax_to_line_items(order, line_items)
    
    try:
        session = stripe.checkout.Session.create(**session_params)
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
def add_to_cart(request: HttpRequest, item_id: int) -> JsonResponse:
    item = get_object_or_404(Item, id=item_id)
    order = get_order_from_session(request) or create_order_and_save_to_session(request)
    order_item, created = OrderItem.objects.get_or_create(order=order, item=item)

    if not created:
        return JsonResponse({
            "ok": False,
            "already_in_cart": True,
            "item_name": item.name,
        })

    return JsonResponse({
        "ok": True,
        "order_id": order.id,
        "item_id": item.id,
        "item_name": item.name,
    })


def cart_page(request: HttpRequest) -> HttpResponse:
    order = get_order_from_session(request)
    
    context = {
        "order": order,
        "order_items": order.order_items.select_related("item").all() if order else [],
        "stripe_pk": settings.STRIPE_PUBLISHABLE_KEY if order else None,
    }
    
    return render(request, "items/order.html", context)


@require_POST
def change_quantity(request: HttpRequest, order_id: int, item_id: int) -> JsonResponse | HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, order=order, item_id=item_id)

    try:
        data = json.loads(request.body.decode() or "{}")
        quantity = int(data.get("quantity", order_item.quantity))
    except (json.JSONDecodeError, ValueError):
        quantity = int(request.POST.get("quantity", order_item.quantity))

    if quantity <= 0:
        order_item.delete()
    else:
        order_item.quantity = quantity
        order_item.save()

    if request.headers.get("accept", "").find("application/json") != -1:
        return JsonResponse({"ok": True, "quantity": quantity})
    
    return redirect("cart_page")


@require_POST
def delete_item(request: HttpRequest, order_id: int, item_id: int) -> JsonResponse | HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, order=order, item_id=item_id)
    order_item.delete()

    if request.headers.get("accept", "").find("application/json") != -1:
        return JsonResponse({"ok": True})
    
    return redirect("cart_page")


@require_POST
def buy_order(request: HttpRequest, order_id: int) -> JsonResponse:
    order = get_object_or_404(Order, id=order_id)
    
    if not order.order_items.exists():
        return JsonResponse({"error": "Cart is empty"}, status=400)
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    line_items = build_line_items(order)
    
    session_params = {
        'payment_method_types': ['card'],
        'line_items': line_items,
        'mode': 'payment',
        'success_url': request.build_absolute_uri(f'/success.html?order_id={order.id}'),
        'cancel_url': request.build_absolute_uri('/cancel.html'),
    }
    
    apply_discount_to_session(order, session_params)
    apply_tax_to_line_items(order, line_items)
    
    try:
        session = stripe.checkout.Session.create(**session_params)
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def success_page(request):
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            order.is_paid = True
            order.save()
        except Order.DoesNotExist:
            pass
    
    return render(request, 'success.html')


def cancel_page(request):
    return render(request, 'cancel.html')