from django.urls import path, include

urlpatterns = [
    path('products/', include('products.urls')),
    path('services/', include('services.urls')),
    # Hier komen later andere app URLs
]