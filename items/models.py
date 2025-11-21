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
