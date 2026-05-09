from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from . import models
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


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


@api_view(['POST'])
def register(request):
    serializers = UserSerializer(data=request.data)
    if serializers.is_valid():
        user = serializers.save()
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh' : str(refresh),
            'access' : str(refresh.access_token)
        }
        return Response(tokens, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

# Endpoint restful para pedidos
# @api_view(['GET', 'POST', 'PATCH'])
# def pedidos(request):
#     pass

# Endpoint restful para favoritos
# @api_view(['GET', 'POST'])
# def pedidos(request):
#     pass
