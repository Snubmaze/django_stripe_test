from django.urls import path
from . import views

urlpatterns = [
    path('items/<int:item_id>/', views.item_page, name='item_page'),
    path('buy/<int:item_id>/', views.buy_item, name='buy_item'),
]