from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager


class State(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.name} de {self.state.name}'

class College(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.name} de {self.city.name}'


class FoodType(models.Model):
    type_name = models.CharField(max_length=100)
    type_icon = models.CharField(max_length=15)
    def __str__(self):
        return self.type_name

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=1)
    background_image_url = models.URLField()
    food_types = models.ForeignKey('FoodType',on_delete=models.SET_NULL,null=True,related_name='restaurants')
    min_order = models.DecimalField(max_digits=6, decimal_places=2)
    avg_min_time = models.IntegerField()
    avg_max_time = models.IntegerField()

    users_who_favorite = models.ManyToManyField(settings.AUTH_USER_MODEL,through='Favorite')

    college = models.ForeignKey(College,on_delete=models.SET_NULL,null=True,related_name='restaurant_college')

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
    img_url = models.URLField()
    food_types = models.ForeignKey('FoodType', on_delete=models.SET_NULL,null=True,related_name='food_types')
    def __str__(self):
        return f'{self.name} ({self.restaurant.name})'

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'restaurant')

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class UserWithEmail(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return self.email

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Carrinho de {self.user.email}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food,on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('cart', 'food')

    def __str__(self):
        return f'{self.quantity} x {self.food.name} for {self.cart.user.email}'

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_number = models.IntegerField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default="Recebido")
    def __str__(self):
        return f'Pedido {self.order_number} de: {self.user.email}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.quantity}x {self.food.name} no Pedido #{self.order.order_number}'

