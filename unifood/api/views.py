from .serializers import *
from . import models
from django.http import JsonResponse


ENSURE_ASCII = {'ensure_ascii': False}

def get_restaurants(request):
    data = models.Restaurant.objects.all()
    serialized = RestaurantsSerializer(data, many=True)
    return JsonResponse({'restaurants':serialized.data},json_dumps_params=ENSURE_ASCII)

def get_food_types(request):
    data = models.FoodType.objects.all()
    serialized = FoodTypesSerializer(data, many=True)
    return JsonResponse({'foodTypes': serialized.data})

def get_restaurant(request, id):
    data = models.Restaurant.objects.get(id=id)
    serialized = RestaurantsSerializer(data)
    return JsonResponse(serialized.data,json_dumps_params=ENSURE_ASCII)

def get_restaurant_foods(request, id):
    data = models.Food.objects.filter(restaurant_id=id)
    serialized = FoodSerializer(data, many=True)
    return JsonResponse({'foods': serialized.data})
