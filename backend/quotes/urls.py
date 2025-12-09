# quotes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuoteDocumentViewSet

router = DefaultRouter()
router.register(r'documents', QuoteDocumentViewSet, basename='quotedocument')

urlpatterns = [
    path('', include(router.urls)),
]