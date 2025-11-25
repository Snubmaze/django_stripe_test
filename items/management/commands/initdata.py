# items/management/commands/initdata.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from items.models import Item, Order, OrderItem

class Command(BaseCommand):
    help = "Create initial test data (idempotent)."

    def handle(self, *args, **options):
        # Примеры айтемов
        items_data = [
            {"name": "Test Product A", "description": "Demo A", "price": 1000},  # cents
            {"name": "Test Product B", "description": "Demo B", "price": 2500},
            {"name": "Test Product C", "description": "Demo C", "price": 499},
        ]
        created_items = []
        for d in items_data:
            item, created = Item.objects.get_or_create(
                name=d["name"],
                defaults={
                    "description": d["description"],
                    "price": d["price"],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Item: {item.name}"))
            created_items.append(item)

        # Пример тестового заказа (корзины)
        order, created = Order.objects.get_or_create(created_at__isnull=True, defaults={})
        # лучше проверять по какому-то флагу — можно использовать метку в metadata, или искать пустой unpaid order
        if created or not order.order_items.exists():
            # удалим старые позиции для простоты (опционально)
            OrderItem.objects.filter(order=order).delete()
            # добавим пару позиций
            for item in created_items[:2]:
                OrderItem.objects.create(order=order, item=item, quantity=1)
            self.stdout.write(self.style.SUCCESS(f"Created sample order #{order.id}"))

        self.stdout.write(self.style.SUCCESS("initdata complete"))
