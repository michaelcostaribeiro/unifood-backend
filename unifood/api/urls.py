"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('api/restaurants/', views.get_restaurants),
    path('api/types', views.get_food_types),
    path('api/restaurant/<int:id>',views.get_restaurant),
    path('api/foods/<int:id>',views.get_restaurant_foods),
    path('api/register/', views.register),
    path('api/user/', views.get_user_info, name='get_user_info'),
    path('api/favorites/', views.favorites, name='favorites'),
    path('api/favorite/<int:id>', views.favorite, name='favorite'),
]
