from django.contrib import admin
from . import models


admin.site.register(models.FoodType)
admin.site.register(models.Restaurant)
admin.site.register(models.Food)
admin.site.register(models.Favorite)