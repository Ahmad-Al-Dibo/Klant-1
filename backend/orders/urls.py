from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    OrderViewSet,
    OrderItemViewSet,
    PaymentViewSet,
    OrderTagViewSet,
    OrderAttachmentViewSet
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'tags', OrderTagViewSet, basename='order-tag')
router.register(r'attachments', OrderAttachmentViewSet, basename='order-attachment')

urlpatterns = [
    path('', include(router.urls)),
    
    # Extra endpoints
    path('orders/<uuid:pk>/items/', OrderViewSet.as_view({'get': 'items'}), name='order-items-list'),
    path('orders/<uuid:pk>/payments/', OrderViewSet.as_view({'get': 'payments'}), name='order-payments-list'),
    path('orders/<uuid:pk>/history/', OrderViewSet.as_view({'get': 'history'}), name='order-history'),
    path('orders/stats/', OrderViewSet.as_view({'get': 'stats'}), name='order-stats'),
    path('orders/dashboard/', OrderViewSet.as_view({'get': 'dashboard'}), name='order-dashboard'),
    
    # Order acties
    path('orders/<uuid:pk>/confirm/', OrderViewSet.as_view({'post': 'confirm'}), name='order-confirm'),
    path('orders/<uuid:pk>/start-processing/', OrderViewSet.as_view({'post': 'start_processing'}), name='order-start-processing'),
    path('orders/<uuid:pk>/mark-shipped/', OrderViewSet.as_view({'post': 'mark_as_shipped'}), name='order-mark-shipped'),
    path('orders/<uuid:pk>/mark-delivered/', OrderViewSet.as_view({'post': 'mark_as_delivered'}), name='order-mark-delivered'),
    path('orders/<uuid:pk>/cancel/', OrderViewSet.as_view({'post': 'cancel'}), name='order-cancel'),
    path('orders/<uuid:pk>/complete/', OrderViewSet.as_view({'post': 'complete'}), name='order-complete'),
    
    # Order item acties
    path('order-items/<uuid:pk>/mark-delivered/', OrderItemViewSet.as_view({'post': 'mark_delivered'}), name='order-item-mark-delivered'),
]

app_name = 'orders_v1'