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
    food_types = slug_field_factory('type_name', many=False)

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
    food_types = slug_food_type

    class Meta:
        model = Food
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user
