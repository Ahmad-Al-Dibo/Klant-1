# project/urls.py (of waar je hoofd urls.py staat)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    # Apps URLs - ZORG DAT DEZE APPS BESTAAN
    path('products/', include('products.urls'), name='products'),
    path('services/', include('services.urls'), name='services'),
    path('auth/', include('authentication.urls')),
    path('clients/', include('clients.urls')),
    path('quotes/', include('quotes.urls')),
    path('orders/', include('orders.urls')),  # Als je orders app hebt
    path('contact/', include('contact.urls')),  # Als je contact app hebt
]

