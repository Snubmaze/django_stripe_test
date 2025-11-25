from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Create initial test data (idempotent)."

    def handle(self, *args, **options):
        from items.models import Item, Order, OrderItem
        
        items_data = [
            {"name": "Sony PlayStation 5", "description": "Sony game console", "price": 38900},
            {"name": "Apple AirPods Max", "description": "Apple headphones", "price": 23000},
            {"name": "Apple MacBookAir 2020", "description": "Apple laptop", "price": 89900},
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

        order, created = Order.objects.get_or_create(id=1, defaults={})
        if created or not order.order_items.exists():
            OrderItem.objects.filter(order=order).delete()
            for item in created_items[:2]:
                OrderItem.objects.create(order=order, item=item, quantity=1)
            self.stdout.write(self.style.SUCCESS(f"Created sample order #{order.id}"))

        self.stdout.write(self.style.SUCCESS("initdata complete"))