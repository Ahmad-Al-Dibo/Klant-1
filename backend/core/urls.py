

from django.urls import include, path
from .views import home_view

urlpatterns = [
    path('home', home_view, name='home')
]