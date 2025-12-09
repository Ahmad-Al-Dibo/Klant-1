from django.urls import path, include

urlpatterns = [
    path('products/', include('products.urls')),
    path('services/', include('services.urls')),
    path('projects/', include("projects.urls")),
]
