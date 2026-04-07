from rest_framework import serializers
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
        if data['avg_min_time']  > data['avg_max_time']:
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