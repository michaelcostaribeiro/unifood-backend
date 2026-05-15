from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from . import models, serializers
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

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def favorites(request):
    if request.method == 'GET':
        favorite_items = Favorite.objects.filter(user=request.user)
        restaurant_ids = []
        for i in favorite_items:
            restaurant_ids.append(i.restaurant_id)
        favorite_restaurants = Restaurant.objects.filter(pk__in=restaurant_ids)
        serializer = RestaurantsSerializer(favorite_restaurants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        restaurant_id = request.data['restaurant']
        user = request.user

        favorite_exists = Favorite.objects.filter(user=user, restaurant=restaurant_id)

        if favorite_exists.exists():
            favorite_exists.delete()
            return Response({'status': 'removed'}, status=status.HTTP_200_OK)
        else:
            serializer = serializers.FavoriteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response({'status': 'created'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorite(request, id):
    data = Favorite.objects.filter(user=request.user, restaurant=id)
    serializer = serializers.FavoriteSerializer(data, many=True)
    if serializer:
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_item(request):
    cart, created = models.Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        models.CartItem.objects.get_or_create(cart=cart, food=request.data['food'], quantity=request.data['quantity'])
        return Response({'status':'item adicionado'}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_items(request):
    user_cart = Cart.objects.get(user=request.user)
    quantities = CartItem.objects.filter(cart=user_cart)
    serializer = serializers.CartItemsSerializer(quantities, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

    # if request.method == 'GET':
    #     favorite_items = Favorite.objects.filter(user=request.user)
    #     restaurant_ids = []
    #     for i in favorite_items:
    #         restaurant_ids.append(i.restaurant_id)
    #     favorite_restaurants = Restaurant.objects.filter(pk__in=restaurant_ids)
    #     serializer = RestaurantsSerializer(favorite_restaurants, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)


