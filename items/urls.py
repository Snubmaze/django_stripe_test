from django.urls import path
from . import views

urlpatterns = [
    path('items/<int:item_id>/', views.item_page, name='item_page'),
    path('buy/<int:item_id>/', views.buy_item, name='buy_item'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('cart/change/<int:order_id>/<int:item_id>/', views.change_quantity, name='change_quantity'),
    path('cart/delete/<int:order_id>/<int:item_id>/', views.delete_item, name='delete_from_cart'),
    path('buy-order/<int:order_id>/', views.buy_order, name='buy_order'),
]