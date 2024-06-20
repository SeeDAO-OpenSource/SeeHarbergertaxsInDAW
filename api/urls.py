from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')
router.register(r'advertise', views.AdvertiseViewSet, basename='advertise')
router.register(r'image', views.imageViewSet, basename='image')




urlpatterns = [
    path('', include(router.urls)),
]
