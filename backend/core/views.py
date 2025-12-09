from django.forms.models import model_to_dict
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from products.models import Product

# Create your views here.
@api_view(['GET'])
def home_view(request): 
    print("Home view accessed")
    products = list(Product.objects.all().values())
    return render(request, 'core/home.html', {'products': products})
