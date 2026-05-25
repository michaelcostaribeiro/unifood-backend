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
from django.db import transaction
import random
from decimal import Decimal


ENSURE_ASCII = {'ensure_ascii': False}

def get_restaurants(request):
    college_id = request.GET.get('college_id')

    if college_id:
        data = models.Restaurant.objects.filter(college_id=college_id)
        serialized = RestaurantsSerializer(data, many=True)
        return JsonResponse({'restaurants':serialized.data},json_dumps_params=ENSURE_ASCII)
    else:
        return JsonResponse({'error': 'college_id is required'}, status=400)

def get_food_types(request):
    data = models.FoodType.objects.all()
    serialized = FoodTypesSerializer(data, many=True)
    return JsonResponse({'foodTypes': serialized.data})

def get_restaurant(request, id):
    data = models.Restaurant.objects.get(id=id)
    serialized = RestaurantsSerializer(data)
    return JsonResponse(serialized.data,json_dumps_params=ENSURE_ASCII)

def get_restaurant_foods(request, id):
    all_restaurant_foods = models.Food.objects.filter(restaurant_id=id)
    food_types = []
    for food in all_restaurant_foods:
        food_types.append(food.food_types)
    unique_food_types = list(set(food_types))
    serialized_food_types = FoodTypesSerializer(unique_food_types, many=True)
    print(food_types)

    serialized = FoodSerializer(all_restaurant_foods, many=True)
    return JsonResponse({'foods': serialized.data,
                         'foodTypes': serialized_food_types.data})


@api_view(['POST'])
def register(request):
    request.data['first_name'] = request.data['first_name'].title()
    request.data['last_name'] = request.data['last_name'].title()
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
        current_cart_item, created = models.CartItem.objects.get_or_create(cart=cart, food_id=request.data['food'], defaults={'quantity': 1})
        if not created:
            if request.data['add_or_delete'] == 'add':
                current_cart_item.quantity += 1
                current_cart_item.save()
            elif request.data['add_or_delete'] == 'delete' and current_cart_item.quantity > 0:
                current_cart_item.quantity -= 1
                current_cart_item.save()
            if current_cart_item.quantity == 0:
                current_cart_item.delete()
        return Response({'status':f'current_cart_item {current_cart_item.quantity}'}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_items(request):
    user_cart = Cart.objects.get(user=request.user)
    quantities = CartItem.objects.filter(cart=user_cart)
    serializer = serializers.CartItemsSerializer(quantities, many=True)
    foods_and_quantity = []
    for item in serializer.data:
        food_instance = Food.objects.get(pk=item['food'])
        food_data = serializers.FoodSerializer(food_instance).data

        foods_and_quantity.append({
            'quantity':item['quantity'],
            'item':food_data})
    return Response(foods_and_quantity, status=status.HTTP_200_OK)

    # if request.method == 'GET':
    #     favorite_items = Favorite.objects.filter(user=request.user)
    #     restaurant_ids = []
    #     for i in favorite_items:
    #         restaurant_ids.append(i.restaurant_id)
    #     favorite_restaurants = Restaurant.objects.filter(pk__in=restaurant_ids)
    #     serializer = RestaurantsSerializer(favorite_restaurants, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_college(request):
    colleges = College.objects.all()
    serializer = CollegeSerializer(colleges, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_restaurant(request):
    try:
        user_cart = Cart.objects.get(user=request.user)

        cart_items = CartItem.objects.filter(cart=user_cart)

        if cart_items.exists():
            first_item = cart_items.first()

            current_restaurant = first_item.food.restaurant

            serializer = serializers.RestaurantSerializer(current_restaurant)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({"message": "O carrinho está vazio."}, status=status.HTTP_204_NO_CONTENT)

    except Cart.DoesNotExist:
        return Response({"error": "Carrinho não encontrado."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        with transaction.atomic():
            user_cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=user_cart)

            if not cart_items.exists():
                return Response({"error": "Seu carrinho está vazio."}, status=status.HTTP_400_BAD_REQUEST)

            while True:
                random_number = random.randint(1000, 9999)
                if not Order.objects.filter(order_number=random_number, finished=False).exists():
                    break

            new_order = Order.objects.create(
                user=request.user,
                order_number=random_number,
                status="Recebido",
                finished=False
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=new_order,
                    food=cart_item.food,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.food.price  # Trava o preço atual
                )

            total_dos_itens = sum(item.food.price * item.quantity for item in cart_items)
            total_com_taxa = total_dos_itens + Decimal('2.00')

            cart_items.delete()

            return Response({
                "message": "Pedido realizado com sucesso!",
                "order_number": new_order.order_number,
                "status": new_order.status,
                "total_pago": float(total_com_taxa)
            }, status=status.HTTP_201_CREATED)

    except Cart.DoesNotExist:
        return Response({"error": "Carrinho não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Erro ao processar pedido: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Erro ao buscar pedidos: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_detail(request, pk):
    try:
        order = Order.objects.get(pk=pk, user=request.user)

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Order.DoesNotExist:
        return Response({"error": "Pedido não encontrado ou acesso negado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Erro ao buscar detalhes: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)