from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
import stripe
from .models import Item
from django.conf import settings


def item_page(request, item_id) -> HttpResponse:
    item = get_object_or_404(Item, id=item_id)
    data = {
        "item": item,
        "stripe_pk": settings.STRIPE_PUBLISHABLE_KEY,
        }
    return render(request, 'items/item.html', context=data)


def buy_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': item.price,   # цена в центах
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                },
                'quantity': 1,
            }],
            success_url='http://127.0.0.1:8000/success.html',
            cancel_url='http://127.0.0.1:8000/cancel.html',
        )
    except Exception as e:
        return HttpResponse(f"Stripe error: {e}", status=500)

    return JsonResponse({"id": session.id})

