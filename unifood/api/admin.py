from django.contrib import admin
from . import models


admin.site.register(models.FoodType)
admin.site.register(models.Restaurant)
admin.site.register(models.Food)
admin.site.register(models.Favorite)
admin.site.register(models.UserWithEmail)
admin.site.register(models.Cart)
admin.site.register(models.CartItem)
admin.site.register(models.College)
admin.site.register(models.City)
admin.site.register(models.State)