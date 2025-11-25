from django.db import models


class Item(models.Model):    
    name = models.CharField(max_length=60)
    description = models.TextField(max_length=1000, blank=True)
    price = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.name

    @property
    def price_dollars(self) -> float:
        return self.price / 100


class Discount(models.Model):
    PERCENTAGE = 'percentage'
    FIXED = 'fixed'
    
    TYPE_CHOICES = [
        (PERCENTAGE, 'Percentage'),
        (FIXED, 'Fixed Amount'),
    ]
    
    name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=PERCENTAGE)
    value = models.PositiveIntegerField()
    stripe_coupon_id = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        if self.discount_type == self.PERCENTAGE:
            return f"{self.name} ({self.value}%)"
        return f"{self.name} (${self.value / 100:.2f})"

    def calculate_amount(self, subtotal: int) -> int:
        if self.discount_type == self.PERCENTAGE:
            return int(subtotal * self.value / 100)
        return min(self.value, subtotal)


class Tax(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    stripe_tax_rate_id = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.percentage}%)"

    def calculate_amount(self, subtotal: int) -> int:
        return int(subtotal * float(self.percentage) / 100)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField(Item, through='OrderItem', related_name='orders')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    is_paid = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Order #{self.id}"

    @property
    def subtotal(self) -> int:
        return sum(oi.item.price * oi.quantity for oi in self.order_items.select_related("item").all())

    @property
    def discount_amount(self) -> int:
        if self.discount and self.discount.is_active:
            return self.discount.calculate_amount(self.subtotal)
        return 0

    @property
    def subtotal_after_discount(self) -> int:
        return self.subtotal - self.discount_amount

    @property
    def tax_amount(self) -> int:
        if self.tax and self.tax.is_active:
            return self.tax.calculate_amount(self.subtotal_after_discount)
        return 0

    @property
    def total(self) -> int:
        return self.subtotal_after_discount + self.tax_amount

    @property
    def total_dollars(self) -> float:
        return self.total / 100.0

    @property
    def subtotal_dollars(self) -> float:
        return self.subtotal / 100.0

    @property
    def discount_amount_dollars(self) -> float:
        return self.discount_amount / 100.0

    @property
    def tax_amount_dollars(self) -> float:
        return self.tax_amount / 100.0


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("order", "item")

    def __str__(self) -> str:
        return f"{self.quantity} × {self.item.name}"