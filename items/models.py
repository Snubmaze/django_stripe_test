from django.db import models
from datetime import datetime


class Item(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=1000)
    price = models.PositiveIntegerField()

    @property
    def price_dollars(self) -> float:
        return self.price / 100
    
    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField("Item", through="OrderItem", related_name="orders")
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id}"

    @property
    def total_cents(self):
        total = 0
        for oi in self.order_items.select_related("item").all():
            total += oi.item.price * oi.quantity
        return total

    @property
    def total_dollars(self):
        return self.total_cents / 100.0


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("order", "item")

    def __str__(self):
        return f"{self.quantity} × {self.item.name}"