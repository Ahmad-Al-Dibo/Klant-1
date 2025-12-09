from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryViewSet, ProductViewSet,
    ProductSearchView, ProductReviewViewSet,
    ProductStatisticsView
)

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet, basename='product-category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ProductReviewViewSet, basename='product-review')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', ProductSearchView.as_view(), name='product-search'),
    path('statistics/', ProductStatisticsView.as_view(), name='product-statistics'),
]