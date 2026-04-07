from django.core.exceptions import ValidationError
from django.db import models

class FoodType(models.Model):
    type_name = models.CharField(max_length=100)
    type_icon = models.CharField(max_length=15)
    def __str__(self):
        return self.type_name

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=1)
    background_image_url = models.URLField()
    food_types = models.OneToOneField('FoodType',on_delete=models.SET_NULL,null=True,related_name='restaurant_food_type')
    min_order = models.DecimalField(max_digits=6, decimal_places=2)
    avg_min_time = models.IntegerField()
    avg_max_time = models.IntegerField()

    def clean(self):
        super().clean()

        if self.avg_min_time is not None and self.avg_max_time is not None:
            if self.avg_min_time > self.avg_max_time:
                raise ValidationError({'avg_min_time': 'O tempo mínimo não pode ser maior que o tempo máximo.'})


    def __str__(self):
        return self.name

class Food(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='foods')
    food_types = models.ManyToManyField(FoodType)
    def __str__(self):
        return f'{self.name} ({self.restaurant.name})'