from django.db import models

# Create your models here.
class Restaurant(models.Model):
    RESTAURANT_TYPE = [
        ('italian', 'Italian'),
        ('mexican', 'Mexican'),
        ('chinese', 'Chinese'),
        ('american', 'American'),
        ('french', 'French'),
        ('indian', 'Indian'),
        ('thai', 'Thai'),
    ]
    name = models.CharField(max_length=100)
    restaurant_type = models.CharField(max_length=20, choices=RESTAURANT_TYPE)
    date_opened = models.DateField()

    def __str__(self):
        return self.name

class Sale(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='sales')
    income = models.DecimalField(max_digits=10, decimal_places=2)
    expenditure = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def profit(self):
        return self.income - self.expenditure
    