from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True, max_length=500)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.title