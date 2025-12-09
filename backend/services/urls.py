from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceCategoryViewSet, ServiceViewSet,
    ServiceSearchView, TestimonialViewSet,
    ServiceStatisticsView
)
app_name = 'services'  # <-- Add this line
router = DefaultRouter()
router.register(r'categories', ServiceCategoryViewSet, basename='service-category')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'testimonials', TestimonialViewSet, basename='testimonial')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', ServiceSearchView.as_view(), name='service-search'),
    path('statistics/', ServiceStatisticsView.as_view(), name='service-statistics'),
]