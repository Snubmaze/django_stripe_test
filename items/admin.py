from django.contrib import admin
from .models import Item, Order, OrderItem, Tax, Discount


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price_dollars")
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("item", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "is_paid", "discount", "tax", "total_dollars")
    list_filter = ("is_paid", "created_at")
    readonly_fields = ("created_at", "subtotal_dollars", "discount_amount_dollars", "tax_amount_dollars", "total_dollars")
    inlines = [OrderItemInline]
    
    fieldsets = (
        (None, {
            "fields": ("created_at", "is_paid", "discount", "tax")
        }),
        ("Totals", {
            "fields": ("subtotal_dollars", "discount_amount_dollars", "tax_amount_dollars", "total_dollars"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "discount_type", "value", "is_active")
    list_filter = ("discount_type", "is_active")
    list_editable = ("is_active",)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "percentage", "is_active")
    list_filter = ("is_active",)
    list_editable = ("is_active",)