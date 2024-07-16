from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'holder', views.HolderViewSet, basename='holder')
router.register(r'advertise', views.AdvertiseViewSet, basename='advertise')
router.register(r'audit', views.AuditViewSet, basename="audit")
router.register(r'image', views.ImageViewSet, basename='image')
router.register(r'login', views.LoginViewSet, basename='login')




urlpatterns = [
    path('', include(router.urls)),
]
