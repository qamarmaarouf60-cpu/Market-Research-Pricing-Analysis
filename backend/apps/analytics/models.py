from django.db import models

class PriceSnapshot(models.Model):
    category = models.CharField(max_length=100)
    avg_price = models.FloatField()
    min_price = models.FloatField()
    max_price = models.FloatField()
    count = models.IntegerField()
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.calculated_at}"
