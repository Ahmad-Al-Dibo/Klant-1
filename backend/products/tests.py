from django.test import TestCase

# Create your tests here.

# In Django shell
from products.models import ProductCategory

# Maak basis categorieën
categories = [
    ('Meubels', 'meubels'),
    ('Elektronica', 'elektronica'),
    ('Antiek', 'antiek'),
    ('Keukens', 'keukens'),
    ('Woonkamermeubels', 'woonkamermeubels'),
    ('Slaapkamermeubels', 'slaapkamermeubels'),
]

for name, slug in categories:
    ProductCategory.objects.get_or_create(
        name=name,
        slug=slug,
        defaults={'description': f'Categorie voor {name.lower()}'}
    )

print("Categorieën aangemaakt!")
