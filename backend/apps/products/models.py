from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    price_text = models.CharField(max_length=50)   # "7,975.00 Dhs"
    price_value = models.FloatField()               # 7975.0
    source = models.CharField(max_length=100)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)