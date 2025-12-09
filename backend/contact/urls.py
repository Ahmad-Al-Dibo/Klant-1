from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ContactCategoryViewSet,
    ContactMessageViewSet,
    ContactAttachmentViewSet,
    ContactFormView,
    NewsletterSubscriptionView
)

router = DefaultRouter()
router.register(r'categories', ContactCategoryViewSet, basename='contact-category')
router.register(r'messages', ContactMessageViewSet, basename='contact-message')
router.register(r'attachments', ContactAttachmentViewSet, basename='contact-attachment')

urlpatterns = [
    path('', include(router.urls)),
    
    # Publieke contact form API
    path('form/', ContactFormView.as_view(), name='contact-form'),
    
    # Nieuwsbrief API
    path('newsletter/subscribe/', NewsletterSubscriptionView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', NewsletterSubscriptionView.as_view(), name='newsletter-unsubscribe'),
    
    # Publieke categorie lijst
    path('categories-public/', ContactCategoryViewSet.as_view({'get': 'active'}), name='contact-categories-public'),
    
    # Bericht tracking voor klanten
    path('track/<uuid:uuid>/', ContactMessageViewSet.as_view({'get': 'retrieve'}), name='contact-message-track'),
]

# Voor versie v1
app_name = 'contact_v1'