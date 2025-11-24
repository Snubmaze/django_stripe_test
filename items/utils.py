from typing import Optional, Dict, Any
from django.http import HttpRequest
import stripe

from .models import Order


def get_order_from_session(request: HttpRequest) -> Optional[Order]:
    order_id = request.session.get("order_id")
    if not order_id:
        return None
    
    try:
        return Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return None


def create_order_and_save_to_session(request: HttpRequest) -> Order:
    order = Order.objects.create()
    request.session["order_id"] = order.id
    request.session.modified = True
    return order


def build_line_items(order: Order) -> list[Dict[str, Any]]:
    line_items = []
    for oi in order.order_items.select_related('item').all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': oi.item.name,
                    'description': oi.item.description or '',
                },
                'unit_amount': oi.item.price,
            },
            'quantity': oi.quantity
        })
    return line_items


def apply_discount_to_session(order: Order, session_params: Dict[str, Any]) -> None:
    if not order.discount or not order.discount.is_active:
        return
    
    if order.discount.stripe_coupon_id:
        session_params['discounts'] = [{'coupon': order.discount.stripe_coupon_id}]
    else:
        coupon = create_stripe_coupon(order.discount)
        session_params['discounts'] = [{'coupon': coupon.id}]


def create_stripe_coupon(discount):
    if discount.discount_type == 'percentage':
        return stripe.Coupon.create(
            percent_off=discount.value,
            duration='once',
            name=discount.name
        )
    return stripe.Coupon.create(
        amount_off=discount.value,
        currency='usd',
        duration='once',
        name=discount.name
    )


def apply_tax_to_line_items(order: Order, line_items: list[Dict[str, Any]]) -> None:
    if not order.tax or not order.tax.is_active:
        return
    
    if order.tax.stripe_tax_rate_id:
        tax_rate_id = order.tax.stripe_tax_rate_id
    else:
        tax_rate = stripe.TaxRate.create(
            display_name=order.tax.name,
            percentage=float(order.tax.percentage),
            inclusive=False,
        )
        tax_rate_id = tax_rate.id
    
    for item in line_items:
        item['tax_rates'] = [tax_rate_id]