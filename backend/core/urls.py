from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, home

router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('home', home)
]
