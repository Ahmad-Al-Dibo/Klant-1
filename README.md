# Producten API Documentatie

## Overzicht

De Producten API biedt een complete oplossing voor het beheren en tonen van meubels, elektronische apparaten en antiek voor verkoop. Deze API ondersteunt alle functionaliteit zoals gespecificeerd in de projectvereisten voor "Möbel- & Elektroverkauf".

## API Endpoints

### Product Categorieën

#### Lijst van categorieën
```
GET /api/v1/products/categories/
```

**Parameters:**
- `parent` (optioneel): Filter op parent categorie slug
- `root_only` (optioneel): Toon alleen root categorieën

**Response:**
```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Meubels",
      "slug": "meubels",
      "description": "Categorie voor meubels",
      "image": "/media/product_categories/meubels.jpg",
      "parent": null,
      "is_active": true,
      "display_order": 0,
      "product_count": 15,
      "subcategories": [...],
      "meta_title": "Meubels - Bedrijfsnaam",
      "meta_description": "Breed assortiment meubels",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### Categorie detail
```
GET /api/v1/products/categories/{slug}/
```

#### Producten in categorie
```
GET /api/v1/products/categories/{slug}/products/
```

### Producten

#### Product lijst
```
GET /api/v1/products/products/
```

**Query Parameters:**
- `search`: Zoek in titel, beschrijving, merk, model
- `category`: Filter op categorie slug
- `min_price`: Minimum prijs
- `max_price`: Maximum prijs
- `condition`: Conditie (new, like_new, good, fair, refurbished)
- `brand`: Merk filter
- `material`: Materiaal filter
- `color`: Kleur filter
- `requires_assembly`: Boolean filter
- `delivery_available`: Boolean filter
- `featured`: Toon alleen uitgelichte producten
- `bestseller`: Toon alleen bestsellers
- `on_sale`: Toon alleen producten in aanbieding
- `ordering`: Sorteer op veld (- voor descending)
- `page`: Pagina nummer
- `page_size`: Items per pagina

**Response:**
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/v1/products/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Moderne Eetkamerstoel",
      "slug": "moderne-eetkamerstoel",
      "short_description": "Stijlvolle eetkamerstoel in modern design",
      "categories": [...],
      "primary_image": {
        "id": 1,
        "image": "/media/products/2024/01/stoel.jpg",
        "image_url": "http://localhost:8000/media/products/2024/01/stoel.jpg",
        "alt_text": "Moderne eetkamerstoel",
        "caption": "Eetkamerstoel in zwarte kleur",
        "display_order": 0,
        "is_primary": true
      },
      "price": "149.99",
      "original_price": "179.99",
      "sale_price": "129.99",
      "is_on_sale": true,
      "final_price": "129.99",
      "discount_percentage": 27.78,
      "condition": "new",
      "status": "available",
      "brand": "DesignCorp",
      "model": "Model-AB12",
      "is_featured": true,
      "is_bestseller": false,
      "views_count": 156,
      "avg_rating": 4.5,
      "review_count": 8,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### Product detail
```
GET /api/v1/products/products/{slug}/
```

**Response:**
```json
{
  "id": 1,
  "title": "Moderne Eetkamerstoel",
  "slug": "moderne-eetkamerstoel",
  "short_description": "Stijlvolle eetkamerstoel in modern design",
  "full_description": "Complete beschrijving van het product...",
  "categories": [...],
  "images": [...],
  "features": [
    {
      "id": 1,
      "name": "Materiaal",
      "value": "Hout, Textiel",
      "icon": "fas fa-cube",
      "display_order": 0
    }
  ],
  "price": "149.99",
  "original_price": "179.99",
  "sale_price": "129.99",
  "is_on_sale": true,
  "final_price": "129.99",
  "discount_percentage": 27.78,
  "condition": "new",
  "status": "available",
  "brand": "DesignCorp",
  "model": "Model-AB12",
  "dimensions": "80x50x90 cm",
  "weight": "12.50",
  "material": "Hout, Textiel",
  "color": "Zwart",
  "is_featured": true,
  "is_bestseller": false,
  "views_count": 157,
  "stock_quantity": 8,
  "low_stock_threshold": 5,
  "is_low_stock": false,
  "sku": "PROD-1001",
  "requires_assembly": true,
  "assembly_service_available": true,
  "delivery_available": true,
  "avg_rating": 4.5,
  "review_count": 8,
  "reviews": [...],
  "meta_title": "Moderne Eetkamerstoel - DesignCorp",
  "meta_description": "Stijlvolle eetkamerstoel in zwarte kleur",
  "meta_keywords": "eetkamerstoel, modern, zwart, design",
  "published_at": "2024-01-15T10:00:00Z",
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### Vergelijkbare producten
```
GET /api/v1/products/products/{slug}/similar/
```

#### Uitgelichte producten
```
GET /api/v1/products/products/featured/
```

#### Bestsellers
```
GET /api/v1/products/products/bestsellers/
```

#### Producten in aanbieding
```
GET /api/v1/products/products/on_sale/
```

### Zoeken

#### Geavanceerd zoeken
```
GET /api/v1/products/search/
```

**Parameters:**
- `q`: Zoekterm
- `category`: Categorie slug
- `min_price`: Minimum prijs
- `max_price`: Maximum prijs
- `condition`: Conditie
- `brand`: Merk
- `material`: Materiaal
- `color`: Kleur
- `requires_assembly`: Boolean
- `delivery_available`: Boolean
- `sort_by`: Sorteer op (newest, price_low, price_high, popular, rating)
- `page`: Pagina nummer
- `page_size`: Items per pagina

**Response:**
```json
{
  "count": 15,
  "results": [...],
  "search_params": {
    "q": "stoel",
    "category": "meubels",
    "min_price": "50",
    "max_price": "200"
  }
}
```

### Reviews

#### Lijst van reviews
```
GET /api/v1/products/reviews/
```

**Parameters:**
- `product`: Filter op product slug

#### Review toevoegen
```
POST /api/v1/products/reviews/
```

**Request Body:**
```json
{
  "product": 1,
  "rating": 5,
  "title": "Fantastisch product!",
  "comment": "Zeer tevreden met de kwaliteit en levering.",
  "reviewer_name": "Jan Jansen",
  "reviewer_email": "jan@voorbeeld.nl",
  "is_verified_purchase": true
}
```

#### Review markeren als handig
```
POST /api/v1/products/reviews/{id}/mark_helpful/
```

**Request Body:**
```json
{
  "type": "yes"
}
```

### Statistieken (Admin)

#### Product statistieken
```
GET /api/v1/products/statistics/
```

**Response:**
```json
{
  "total_products": 150,
  "available_products": 125,
  "sold_products": 25,
  "low_stock_products": 8,
  "category_stats": [
    {"name": "Meubels", "product_count": 65},
    {"name": "Elektronica", "product_count": 45},
    {"name": "Antiek", "product_count": 40}
  ],
  "total_revenue": 12500.50
}
```

## Data Modellen

### ProductCategory
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| name | String | Categorie naam |
| slug | String | URL-vriendelijke naam |
| description | Text | Beschrijving |
| image | Image | Categorie afbeelding |
| parent | ForeignKey | Parent categorie |
| is_active | Boolean | Is categorie actief? |
| display_order | Integer | Weergave volgorde |
| meta_title | String | SEO titel |
| meta_description | Text | SEO beschrijving |
| meta_keywords | Text | SEO keywords |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |

### Product
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| title | String | Product titel |
| slug | String | URL-vriendelijke naam |
| short_description | Text | Korte beschrijving |
| full_description | Text | Volledige beschrijving |
| categories | ManyToMany | Categorieën |
| price | Decimal | Prijs (EUR) |
| original_price | Decimal | Originele prijs |
| is_on_sale | Boolean | In aanbieding? |
| sale_price | Decimal | Aanbiedingsprijs |
| sku | String | Stock Keeping Unit |
| stock_quantity | Integer | Voorraad hoeveelheid |
| low_stock_threshold | Integer | Lage voorraad drempel |
| condition | String | Conditie (new, like_new, good, fair, refurbished) |
| status | String | Status (available, sold, reserved, pending) |
| brand | String | Merk |
| model | String | Model |
| dimensions | String | Afmetingen |
| weight | Decimal | Gewicht (kg) |
| material | String | Materiaal |
| color | String | Kleur |
| is_featured | Boolean | Uitgelicht? |
| is_bestseller | Boolean | Bestseller? |
| views_count | Integer | Aantal weergaven |
| requires_assembly | Boolean | Montage nodig? |
| assembly_service_available | Boolean | Montageservice beschikbaar? |
| delivery_available | Boolean | Bezorging beschikbaar? |
| meta_title | String | SEO titel |
| meta_description | Text | SEO beschrijving |
| meta_keywords | Text | SEO keywords |
| created_by | ForeignKey | Aangemaakt door |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |
| published_at | DateTime | Publicatiedatum |

### ProductImage
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| product | ForeignKey | Gerelateerd product |
| image | Image | Afbeelding |
| alt_text | String | Alt tekst |
| caption | String | Bijschrift |
| display_order | Integer | Weergave volgorde |
| is_primary | Boolean | Hoofdafbeelding? |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |

### ProductFeature
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| product | ForeignKey | Gerelateerd product |
| name | String | Kenmerk naam |
| value | String | Kenmerk waarde |
| icon | String | Icoon class |
| display_order | Integer | Weergave volgorde |

### ProductReview
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| product | ForeignKey | Gerelateerd product |
| user | ForeignKey | Gebruiker |
| rating | Integer | Beoordeling (1-5) |
| title | String | Titel |
| comment | Text | Opmerking |
| reviewer_name | String | Naam beoordelaar |
| reviewer_email | Email | Email beoordelaar |
| is_approved | Boolean | Goedgekeurd? |
| is_verified_purchase | Boolean | Geverifieerde aankoop? |
| helpful_yes | Integer | Handig - ja teller |
| helpful_no | Integer | Handig - nee teller |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |

## Filters

### Prijs Filtering
```
GET /api/v1/products/products/?min_price=50&max_price=200
```

### Categorie Filtering
```
GET /api/v1/products/products/?category=meubels
```

### Conditie Filtering
```
GET /api/v1/products/products/?condition=new
```

### Merk Filtering
```
GET /api/v1/products/products/?brand=DesignCorp
```

### Materiaal Filtering
```
GET /api/v1/products/products/?material=hout
```

### Sortering
```
GET /api/v1/products/products/?ordering=-price           # Duurste eerst
GET /api/v1/products/products/?ordering=price            # Goedkoopste eerst
GET /api/v1/products/products/?ordering=-created_at      # Nieuwste eerst
GET /api/v1/products/products/?ordering=-views_count     # Populairste eerst
```

## Authenticatie

### JWT Token Authenticatie
```bash
# Token verkrijgen
POST /api/auth/token/
{
  "email": "gebruiker@voorbeeld.nl",
  "password": "wachtwoord"
}

# Token refresh
POST /api/auth/token/refresh/
{
  "refresh": "refresh_token"
}
```

### Authenticatie Headers
```http
Authorization: Bearer <access_token>
```

## Permissies

| Endpoint | Permissies |
|----------|------------|
| `GET /products/` | Iedereen |
| `POST /products/` | Alleen admin |
| `GET /reviews/` | Iedereen |
| `POST /reviews/` | Ingelogde gebruikers |
| `GET /statistics/` | Alleen admin |

## Rate Limiting

- Publieke endpoints: 100 requests per minuut
- Authenticated endpoints: 1000 requests per minuut
- Admin endpoints: 5000 requests per minuut

## Foutmeldingen

### HTTP Status Codes
| Code | Beschrijving |
|------|-------------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### Error Response Format
```json
{
  "error": {
    "code": "invalid_input",
    "message": "Ongeldige invoer",
    "details": {
      "price": ["Dit veld is verplicht."]
    }
  }
}
```

## Voorbeelden

### Product toevoegen (Admin)
```bash
curl -X POST http://localhost:8000/api/v1/products/products/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nieuwe Meubelset",
    "short_description": "Complete meubelset voor woonkamer",
    "full_description": "Uitgebreide beschrijving...",
    "categories": [1, 2],
    "price": "899.99",
    "stock_quantity": 10,
    "condition": "new",
    "brand": "ModernLiving",
    "material": "Eikenhout",
    "color": "Naturel",
    "requires_assembly": true,
    "delivery_available": true
  }'
```

### Review toevoegen
```bash
curl -X POST http://localhost:8000/api/v1/products/reviews/ \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "rating": 5,
    "title": "Uitstekende kwaliteit!",
    "comment": "Zeer tevreden met het product en de service.",
    "is_verified_purchase": true
  }'
```

### Zoeken met filters
```bash
curl "http://localhost:8000/api/v1/products/search/?q=stoel&category=meubels&min_price=50&max_price=300&condition=new&sort_by=price_low"
```

## Installatie & Configuratie

### Requirements
```bash
# backend/requirements/base.txt
Django>=4.2
djangorestframework>=3.14
djongo>=1.3.6
pymongo>=4.3
djangorestframework-simplejwt>=5.3
python-decouple>=3.8
pillow>=10.0
python-magic>=0.4.27
corsheaders>=3.14
whitenoise>=6.5
django-filter>=23.3
```

### Environment Variables
```env
# .env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=company_services
DB_HOST=localhost
DB_PORT=27017
DB_USER=
DB_PASSWORD=
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Database Migratie
```bash
python manage.py makemigrations products
python manage.py migrate
```

### Test Data
```bash
python scripts/seed_products.py
```

## Testen

### Unit Tests
```bash
python manage.py test products.tests
```

### API Tests
```bash
# Install test requirements
pip install pytest pytest-django

# Run tests
pytest products/tests/ -v
```

### Test Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test products
coverage report
coverage html
```

## Best Practices

### Caching
```python
# Gebruik caching voor veelbezochte endpoints
@method_decorator(cache_page(60 * 15))  # 15 minuten cache
@method_decorator(vary_on_cookie)
def list(self, request):
    ...
```

### Pagination
Standaard pagination: 20 items per pagina
```bash
GET /api/v1/products/products/?page=2&page_size=50
```

### Image Handling
- Maximale afbeeldingsgrootte: 10MB
- Ondersteunde formaten: JPEG, PNG, WebP
- Automatische thumbnail generatie (optioneel)

### SEO Optimalisatie
- Automatische meta tags
- SEO-vriendelijke URLs (slugs)
- Structured data (schema.org)

## Troubleshooting

### Veelvoorkomende problemen

1. **Database connectie fout**
   ```bash
   # Controleer MongoDB service
   sudo service mongod status
   
   # Test connectie
   mongo --host localhost --port 27017
   ```

2. **Permission denied errors**
   - Controleer JWT token
   - Verifieer user permissions
   - Check CORS settings

3. **Image upload fouten**
   - Controleer MEDIA_ROOT permissions
   - Verifieer file size limits
   - Check image format

## Veiligheid

### Security Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

### Input Validatie
- SQL injection protection via Django ORM
- XSS protection via template escaping
- File upload validation
- Rate limiting

### Data Bescherming
- HTTPS verplicht in production
- JWT token expiration
- Password hashing (bcrypt)
- Sensitive data encryption

## Changelog

### Versie 1.0.0 (4 December 2025)
- Initial release
- Complete CRUD voor producten
- Categorie management
- Review systeem
- Geavanceerde zoekfunctionaliteit
- Admin statistieken
- Multi-language support (NL, DE, AR)

## Contact & Support

Voor vragen of ondersteuning:
- API Documentatie: `/docs/`
- Admin Interface: `/admin/`
- GitHub Repository: [link]
- Email: support@bedrijfsnaam.nl

---

*Laatst bijgewerkt: 4 December 2025*
