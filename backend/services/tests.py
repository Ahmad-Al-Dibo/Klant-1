from django.test import TestCase

# Create your tests here.

# In Django shell - Maak basis dienst categorieën
from services.models import ServiceCategory

categories_data = [
    {
        'name': 'Demontage & Montage',
        'category_type': 'demontage_montage',
        'icon': 'fas fa-tools',
        'description': 'Professionele demontage en montage van keukens, meubels en apparaten.',
        'show_on_homepage': True,
    },
    {
        'name': 'Möbel- & Elektroverkauf',
        'category_type': 'mobel_verkauf',
        'icon': 'fas fa-couch',
        'description': 'Verkoop van meubels, elektrische apparaten en antiek.',
        'show_on_homepage': True,
    },
    {
        'name': 'Auto-Ankauf & -Verkauf',
        'category_type': 'auto_ankauf',
        'icon': 'fas fa-car',
        'description': 'Inkoop en verkoop van auto\'s en auto-onderdelen.',
        'show_on_homepage': True,
    },
    {
        'name': 'Autowerkstatt & Karosserie',
        'category_type': 'autowerkstatt',
        'icon': 'fas fa-wrench',
        'description': 'Autoreparaties, karosseriewerk en onderhoud.',
        'show_on_homepage': True,
    },
    {
        'name': 'Renovierung & Wiederaufbau',
        'category_type': 'renovierung',
        'icon': 'fas fa-hammer',
        'description': 'Renovatie van huizen, hotels en fabrieken.',
        'show_on_homepage': True,
    },
    {
        'name': 'Entsorgung',
        'category_type': 'entsorgung',
        'icon': 'fas fa-trash-alt',
        'description': 'Afvoer van meubels, elektronica en voertuigen.',
        'show_on_homepage': True,
    },
    {
        'name': 'Transport & Verpackung',
        'category_type': 'transport',
        'icon': 'fas fa-truck-moving',
        'description': 'Verhuisservice en transport voor woningen en bedrijven.',
        'show_on_homepage': True,
    },
    {
        'name': 'Import & Export',
        'category_type': 'import_export',
        'icon': 'fas fa-globe-europe',
        'description': 'Import/export naar alle Arabische landen.',
        'show_on_homepage': True,
    },
]

for data in categories_data:
    ServiceCategory.objects.get_or_create(
        name=data['name'],
        defaults=data
    )

print(f"{len(categories_data)} dienst categorieën aangemaakt!")