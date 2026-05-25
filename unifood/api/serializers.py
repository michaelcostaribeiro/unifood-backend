from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


def slug_field_factory(slug_field, many=True):
    return serializers.SlugRelatedField(
        many=many,
        read_only=True,
        slug_field=slug_field
    )


slug_food_type = slug_field_factory('type_name')


class RestaurantsSerializer(serializers.ModelSerializer):
    food_types = serializers.ReadOnlyField(source='food_types.type_name')

    class Meta:
        model = Restaurant
        fields = '__all__'

    def validate(self, data):
        if data['avg_min_time'] > data['avg_max_time']:
            raise serializers.ValidationError("O tempo mínimo não pode ser maior que o tempo máximo.")
        return data


class FoodTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    food_types = serializers.ReadOnlyField(source='food_types.type_name')

    class Meta:
        model = Food
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserWithEmail
        fields = ['id', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = UserWithEmail.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Favorite
        fields = '__all__'

class CartItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity','food']

class CollegeSerializer(serializers.ModelSerializer):
    city_name = serializers.ReadOnlyField(source='city.name')

    state_name = serializers.ReadOnlyField(source='city.state.name')
    class Meta:
        model = College
        fields = '__all__'

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            'id',
            'name',
            'score',
            'avg_min_time',
            'avg_max_time',
            'min_order',
            'background_image_url'
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'food', 'quantity', 'price_at_purchase', 'subtotal']

    def get_subtotal(self, obj):
        return float(obj.price_at_purchase * obj.quantity)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_pedido = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'created_at', 'status', 'finished', 'items', 'total_pedido']

    def get_total_pedido(self, obj):
        # Soma o subtotal de todos os itens e adiciona os R$ 2,00 da taxa do app
        total_itens = sum(item.price_at_purchase * item.quantity for item in obj.items.all())
        return float(total_itens + 2)