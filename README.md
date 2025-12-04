# **Producten API Documentatie**

## **Overzicht**

De Producten API biedt een complete oplossing voor het beheren en tonen van meubels, elektronische apparaten en antiek voor verkoop. Deze API ondersteunt alle functionaliteit zoals gespecificeerd in de projectvereisten voor "Möbel- & Elektroverkauf".

## **API Endpoints**

### **Product Categorieën**

#### **Lijst van categorieën**
```
GET /api/v1/products/categories/
```

**Parameters:**
- `parent` (optioneel): Filter op parent categorie slug
- `root_only` (optioneel): Toon alleen root categorieën



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

#### **Categorie detail**
```
GET /api/v1/products/categories/{slug}/
```

#### **Producten in categorie**
```
GET /api/v1/products/categories/{slug}/products/
```

### **Producten**

#### **Product lijst**
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

#### **Product detail**
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

#### **Vergelijkbare producten**
```
GET /api/v1/products/products/{slug}/similar/
```

#### **Uitgelichte producten**
```
GET /api/v1/products/products/featured/
```

#### **Bestsellers**
```
GET /api/v1/products/products/bestsellers/
```

#### **Producten in aanbieding**
```
GET /api/v1/products/products/on_sale/
```

### **Zoeken**

#### **Geavanceerd zoeken**
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

### **Reviews**

#### **Lijst van reviews**
```
GET /api/v1/products/reviews/
```

**Parameters:**
- `product`: Filter op product slug

#### **Review toevoegen**
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

#### **Review markeren als handig**
```
POST /api/v1/products/reviews/{id}/mark_helpful/
```

**Request Body:**
```json
{
  "type": "yes"
}
```

### **Statistieken (Admin)**

#### **Product statistieken**
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

---

# **Diensten API Documentatie**

## **Overzicht**

De Diensten API biedt een complete oplossing voor het beheren en presenteren van alle diensten zoals gespecificeerd in de projectvereisten. Deze API ondersteunt alle 8 hoofdcategorieën: Demontage & Montage, Möbel- & Elektroverkauf, Auto-Ankauf & -Verkauf, Autowerkstatt & Karosserie, Renovierung & Wiederaufbau, Entsorgung, Transport & Verpackung, en Import & Export.

## **API Endpoints**

### **Dienst Categorieën**

#### **Lijst van categorieën**
```
GET /api/v1/services/categories/
```

**Parameters:**
- `homepage` (optioneel): Toon alleen categorieën voor homepage

**Response:**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Demontage & Montage",
      "slug": "demontage-montage",
      "category_type": "demontage_montage",
      "icon": "fas fa-tools",
      "icon_display": "fas fa-tools",
      "description": "Professionele demontage en montage van keukens, meubels en apparaten.",
      "image": "/media/service_categories/demontage.jpg",
      "display_order": 0,
      "is_active": true,
      "show_on_homepage": true,
      "service_count": 5,
      "meta_title": "Demontage & Montage - Bedrijfsnaam",
      "meta_description": "Professionele demontage en montage diensten",
      "meta_keywords": "demontage, montage, keukens, meubels",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Categorie detail**
```
GET /api/v1/services/categories/{slug}/
```

#### **Diensten in categorie**
```
GET /api/v1/services/categories/{slug}/services/
```

### **Diensten**

#### **Dienst lijst**
```
GET /api/v1/services/services/
```

**Query Parameters:**
- `search`: Zoek in naam, beschrijving, voordelen
- `category`: Filter op categorie slug
- `has_fixed_price`: Filter op vaste prijs
- `can_book_online`: Filter op online boekbaar
- `has_emergency_service`: Filter op spoedservice
- `city`: Filter op beschikbare stad
- `popular`: Toon alleen populaire diensten
- `featured`: Toon alleen uitgelichte diensten
- `ordering`: Sorteer op veld (- voor descending)
- `page`: Pagina nummer
- `page_size`: Items per pagina

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/services/services/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Keukenmontage",
      "slug": "keukenmontage",
      "category": {
        "id": 1,
        "name": "Demontage & Montage",
        "slug": "demontage-montage",
        "category_type": "demontage_montage",
        "icon": "fas fa-tools"
      },
      "short_description": "Professionele montage van keukens van alle merken.",
      "primary_image": {
        "id": 1,
        "image": "/media/services/2024/01/keukenmontage.jpg",
        "image_url": "http://localhost:8000/media/services/2024/01/keukenmontage.jpg",
        "caption": "Keukenmontage project",
        "alt_text": "Keukenmontage dienst",
        "is_before_image": false,
        "is_after_image": true,
        "display_order": 0,
        "is_primary": true
      },
      "has_fixed_price": true,
      "fixed_price": "250.00",
      "price_description": "Vanaf €250",
      "estimated_time": "4-8 uur",
      "is_popular": true,
      "is_featured": false,
      "is_active": true,
      "requires_quote": false,
      "can_book_online": true,
      "has_emergency_service": false,
      "views_count": 342,
      "quote_requests_count": 45,
      "faq_count": 8,
      "testimonial_count": 12,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Dienst detail**
```
GET /api/v1/services/services/{slug}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Keukenmontage",
  "slug": "keukenmontage",
  "category": {...},
  "short_description": "Professionele montage van keukens van alle merken.",
  "full_description": "Volledige beschrijving van de keukenmontage dienst...",
  "benefits": "• Snelle en professionele montage\n• Ervaren monteurs\n• Schadevrije installatie\n• Opruimen van verpakkingsmateriaal",
  "process": "1. Eerste inspectie\n2. Offerte opstellen\n3. Planning afspraak\n4. Montage uitvoeren\n5. Nazorg en controle",
  "has_fixed_price": true,
  "fixed_price": "250.00",
  "price_description": "Vanaf €250",
  "estimated_time": "4-8 uur",
  "is_popular": true,
  "is_featured": false,
  "is_active": true,
  "requirements": "• Keukenonderdelen aanwezig\n• Elektriciteit en water aansluiting\n• Voldoende werkruimte",
  "requires_quote": false,
  "can_book_online": true,
  "has_emergency_service": false,
  "views_count": 343,
  "quote_requests_count": 45,
  "faq_count": 8,
  "testimonial_count": 12,
  "images": [...],
  "faqs": [
    {
      "id": 1,
      "question": "Hoe lang duurt een gemiddelde keukenmontage?",
      "answer": "Een gemiddelde keukenmontage duurt 4-8 uur, afhankelijk van de grootte en complexiteit.",
      "display_order": 0,
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "features": [
    {
      "id": 1,
      "title": "Ervaren monteurs",
      "description": "Al onze monteurs hebben minimaal 5 jaar ervaring.",
      "icon": "fas fa-user-check",
      "display_order": 0
    }
  ],
  "packages": [
    {
      "id": 1,
      "name": "Basis Pakket",
      "description": "Standaard montage van keukenkastjes en werkblad.",
      "price": "250.00",
      "duration": "4 uur",
      "includes": "• Montage kastjes\n• Plaatsen werkblad\n• Basis afstelling",
      "excludes": "• Elektra aansluitingen\n• Wateraansluitingen\n• Tegelwerk",
      "is_popular": true,
      "display_order": 0,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "areas": [
    {
      "id": 1,
      "city": "Amsterdam",
      "postal_code": "1011AA",
      "region": "Noord-Holland",
      "is_active": true
    }
  ],
  "testimonials": [...],
  "meta_title": "Keukenmontage - Professionele service",
  "meta_description": "Professionele keukenmontage door ervaren vakmensen",
  "meta_keywords": "keukenmontage, keuken installatie, monteur",
  "published_at": "2024-01-15T10:00:00Z",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

#### **Voor/na afbeeldingen**
```
GET /api/v1/services/services/{slug}/before_after_images/
```

**Response:**
```json
{
  "before_images": [...],
  "after_images": [...]
}
```

#### **Homepage diensten**
```
GET /api/v1/services/services/homepage_services/
```

#### **Populaire diensten**
```
GET /api/v1/services/services/popular/
```

#### **Quote request increment**
```
POST /api/v1/services/services/{slug}/increment_quote_request/
```

### **Zoeken**

#### **Geavanceerd zoeken**
```
GET /api/v1/services/search/
```

**Parameters:**
- `q`: Zoekterm
- `category`: Categorie slug
- `has_fixed_price`: Filter op vaste prijs
- `can_book_online`: Filter op online boekbaar
- `has_emergency_service`: Filter op spoedservice
- `city`: Filter op stad
- `sort_by`: Sorteer op (newest, popular, name, price_low, price_high)
- `page`: Pagina nummer
- `page_size`: Items per pagina

**Response:**
```json
{
  "count": 10,
  "results": [...],
  "search_params": {
    "q": "montage",
    "category": "demontage-montage",
    "city": "Amsterdam"
  }
}
```

### **Testimonials**

#### **Lijst van testimonials**
```
GET /api/v1/services/testimonials/
```

**Parameters:**
- `service`: Filter op service slug
- `featured`: Toon alleen uitgelichte testimonials

#### **Testimonial toevoegen**
```
POST /api/v1/services/testimonials/
```

**Request Body:**
```json
{
  "service": 1,
  "client_name": "Peter de Vries",
  "client_location": "Amsterdam",
  "client_company": "Restaurant De Ster",
  "content": "Uitstekende service! De keuken werd perfect gemonteerd.",
  "rating": 5,
  "project_date": "2024-01-10",
  "project_description": "Keukenmontage restaurant"
}
```

#### **Uitgelichte testimonials**
```
GET /api/v1/services/testimonials/featured/
```

### **Statistieken (Admin)**

#### **Dienst statistieken**
```
GET /api/v1/services/statistics/
```

**Response:**
```json
{
  "total_services": 40,
  "active_services": 35,
  "category_stats": [
    {
      "name": "Demontage & Montage",
      "service_count": 8,
      "active_service_count": 7
    },
    {
      "name": "Auto-Ankauf & -Verkauf",
      "service_count": 6,
      "active_service_count": 5
    }
  ],
  "popular_services": [
    {
      "name": "Keukenmontage",
      "views_count": 342,
      "quote_requests_count": 45
    }
  ],
  "monthly_views": [
    {
      "month": "2024-01-01",
      "views_count": 1245
    }
  ]
}
```

## **Data Modellen**

### **ServiceCategory**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| name | String | Categorie naam |
| slug | String | URL-vriendelijke naam |
| category_type | String | Type categorie (8 vaste types) |
| icon | String | Font Awesome icoon class |
| description | Text | Beschrijving van categorie |
| image | Image | Categorie afbeelding |
| display_order | Integer | Weergave volgorde |
| is_active | Boolean | Is categorie actief? |
| show_on_homepage | Boolean | Toon op homepage? |
| meta_title | String | SEO titel |
| meta_description | Text | SEO beschrijving |
| meta_keywords | Text | SEO keywords |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |

### **Service**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| name | String | Dienst naam |
| slug | String | URL-vriendelijke naam |
| category | ForeignKey | Hoofdcategorie |
| short_description | Text | Korte beschrijving |
| full_description | Text | Volledige beschrijving |
| benefits | Text | Lijst van voordelen |
| process | Text | Werkwijze beschrijving |
| has_fixed_price | Boolean | Heeft vaste prijs? |
| fixed_price | Decimal | Vaste prijs indien van toepassing |
| price_description | String | Prijs beschrijving |
| estimated_time | String | Geschatte tijd |
| is_popular | Boolean | Populaire dienst? |
| is_featured | Boolean | Uitgelichte dienst? |
| is_active | Boolean | Is dienst actief? |
| requirements | Text | Vereisten voor dienst |
| requires_quote | Boolean | Offerte nodig? |
| can_book_online | Boolean | Online boekbaar? |
| has_emergency_service | Boolean | Spoedservice beschikbaar? |
| meta_title | String | SEO titel |
| meta_description | Text | SEO beschrijving |
| meta_keywords | Text | SEO keywords |
| views_count | Integer | Aantal bekeken |
| quote_requests_count | Integer | Aantal offerte aanvragen |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |
| published_at | DateTime | Publicatiedatum |

### **ServiceImage**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| service | ForeignKey | Gerelateerde dienst |
| image | Image | Afbeelding |
| caption | String | Bijschrift |
| alt_text | String | Alternatieve tekst |
| is_before_image | Boolean | Voor afbeelding? |
| is_after_image | Boolean | Na afbeelding? |
| display_order | Integer | Weergave volgorde |
| is_primary | Boolean | Hoofdafbeelding? |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |

### **FAQ**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| service | ForeignKey | Gerelateerde dienst |
| question | String | Vraag |
| answer | Text | Antwoord |
| display_order | Integer | Weergave volgorde |
| is_active | Boolean | Is FAQ actief? |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |

### **ServiceFeature**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| service | ForeignKey | Gerelateerde dienst |
| title | String | Kenmerk titel |
| description | Text | Beschrijving |
| icon | String | Icoon class |
| display_order | Integer | Weergave volgorde |

### **ServicePackage**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| service | ForeignKey | Gerelateerde dienst |
| name | String | Pakket naam |
| description | Text | Beschrijving |
| price | Decimal | Prijs |
| duration | String | Duur |
| includes | Text | Inclusief lijst |
| excludes | Text | Exclusief lijst |
| is_popular | Boolean | Populair pakket? |
| display_order | Integer | Weergave volgorde |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |

### **ServiceArea**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| service | ForeignKey | Gerelateerde dienst |
| city | String | Stad |
| postal_code | String | Postcode |
| region | String | Regio |
| is_active | Boolean | Is gebied actief? |

### **Testimonial**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| service | ForeignKey | Gerelateerde dienst |
| client_name | String | Klant naam |
| client_location | String | Locatie klant |
| client_company | String | Bedrijf klant |
| content | Text | Beoordeling tekst |
| rating | Integer | Beoordeling (1-5) |
| is_approved | Boolean | Goedgekeurd? |
| is_featured | Boolean | Uitgelicht? |
| display_order | Integer | Weergave volgorde |
| project_date | Date | Project datum |
| project_description | String | Project beschrijving |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |

### **ServiceView**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| service | ForeignKey | Gerelateerde dienst |
| user | ForeignKey | Gebruiker (optioneel) |
| session_key | String | Session key |
| ip_address | IP Address | IP adres |
| user_agent | Text | User agent |
| referrer | URL | Referrer URL |
| created_at | DateTime | Aanmaakdatum |

## **Categorie Types**

De API ondersteunt 8 vaste categorie types volgens de specificaties:

| Type | Omschrijving | Icoon |
|------|-------------|-------|
| `demontage_montage` | Demontage & Montage | fas fa-tools |
| `mobel_verkauf` | Möbel- & Elektroverkauf | fas fa-couch |
| `auto_ankauf` | Auto-Ankauf & -Verkauf | fas fa-car |
| `autowerkstatt` | Autowerkstatt & Karosserie | fas fa-wrench |
| `renovierung` | Renovierung & Wiederaufbau | fas fa-hammer |
| `entsorgung` | Entsorgung | fas fa-trash-alt |
| `transport` | Transport & Verpackung | fas fa-truck-moving |
| `import_export` | Import & Export | fas fa-globe-europe |

## **Filters**

### **Stad Filtering**
```
GET /api/v1/services/services/?city=Amsterdam
```

### **Categorie Filtering**
```
GET /api/v1/services/services/?category=demontage-montage
```

### **Online Boekbaar Filtering**
```
GET /api/v1/services/services/?can_book_online=true
```

### **Spoedservice Filtering**
```
GET /api/v1/services/services/?has_emergency_service=true
```

### **Sortering**
```
GET /api/v1/services/services/?ordering=-views_count     # Populairste eerst
GET /api/v1/services/services/?ordering=name             # Naam A-Z
GET /api/v1/services/services/?ordering=-fixed_price     # Duurste eerst
GET /api/v1/services/services/?ordering=fixed_price      # Goedkoopste eerst
```

## **Authenticatie & Permissies**

### **JWT Token Authenticatie**
```bash
# Token verkrijgen
POST /api/auth/token/
{
  "email": "gebruiker@voorbeeld.nl",
  "password": "wachtwoord"
}

# Authenticatie Header
Authorization: Bearer <access_token>
```

### **Permissies Overzicht**
| Endpoint | Permissies |
|----------|------------|
| `GET /services/` | Iedereen |
| `POST /services/` | Alleen admin |
| `GET /testimonials/` | Iedereen |
| `POST /testimonials/` | Iedereen (auto-moderation voor niet-admin) |
| `GET /statistics/` | Alleen admin |
| `POST /increment_quote_request/` | Iedereen (voor offerte tracking) |

## **Business Workflows**

### **1. Dienst Weergave Tracking**
```python
# Automatisch bij elke GET request naar service detail
service.increment_views()
ServiceView.objects.create(
    service=service,
    user=request.user if authenticated else None,
    ip_address=client_ip,
    user_agent=request.META.get('HTTP_USER_AGENT', '')
)
```

### **2. Testimonial Moderation Workflow**
```python
# Niet-admin gebruikers: testimonial wacht op goedkeuring
# Admin gebruikers: testimonial direct goedgekeurd
if request.user.is_staff:
    testimonial.is_approved = True
    testimonial.save()
else:
    # Stuur email naar admin voor review
    send_moderation_email(testimonial)
```

### **3. Voor/Na Portfolio Systeem**
```python
# Speciale endpoints voor before/after images
before_images = service.images.filter(is_before_image=True)
after_images = service.images.filter(is_after_image=True)
# Gebruikt voor renovatie en reparatie diensten
```

### **4. Dienst Pakketten Systeem**
```python
# Verschillende pakketten per dienst
packages = service.packages.all()
# Voorbeelden: Basis, Standard, Premium pakketten
# Elk met eigen prijs, duur en inclusies
```

## **Integratie Voorbeelden**

### **Frontend Integratie**
```javascript
// Dienst detail ophalen
fetch('/api/v1/services/services/keukenmontage/')
  .then(response => response.json())
  .then(data => {
    console.log(data.name); // "Keukenmontage"
    console.log(data.packages[0].price); // "250.00"
  });

// Testimonial toevoegen
fetch('/api/v1/services/testimonials/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    service: 1,
    client_name: 'Jan Jansen',
    content: 'Uitstekende service!',
    rating: 5
  })
});
```

### **Offerte Systeem Integratie**
```python
# Bij offerte aanvraag, increment de teller
service = Service.objects.get(slug='keukenmontage')
service.increment_quote_requests()

# Link naar quotes API voor complete offerte workflow
POST /api/v1/quotes/requests/
{
  "service": 1,
  "customer_name": "Jan Jansen",
  "customer_email": "jan@voorbeeld.nl",
  "description": "Keukenmontage nodig voor nieuwe keuken"
}
```

## **SEO Optimalisatie**

### **Automatische SEO Velden**
- **Slug generation**: URL-vriendelijke namen
- **Meta tags**: Title, description, keywords per dienst
- **Structured data**: Schema.org markup ready
- **Sitemap integration**: Automatische sitemap generatie

### **SEO Best Practices**
```python
# Automatische slug generatie
slug = slugify(service.name)

# Meta tag fallback
if not service.meta_title:
    service.meta_title = f"{service.name} - {service.category.name}"
if not service.meta_description:
    service.meta_description = service.short_description[:160]
```

## **Performance Optimalisatie**

### **Query Optimization**
```python
# Gebruik select_related en prefetch_related
services = Service.objects.select_related('category') \
    .prefetch_related(
        'images',
        'faqs',
        'packages',
        'areas',
        'testimonials'
    ) \
    .filter(is_active=True)
```

### **Caching Strategie**
```python
# Cache vaak bezochte endpoints
@method_decorator(cache_page(60 * 30))  # 30 minuten
def list(self, request):
    return super().list(request)

# Cache homepage services langer
@method_decorator(cache_page(60 * 60))  # 60 minuten
def homepage_services(self, request):
    # ...
```

## **Error Handling**

### **HTTP Status Codes**
| Code | Beschrijving | Voorbeeld |
|------|-------------|-----------|
| 200 | OK | Succesvolle request |
| 201 | Created | Resource aangemaakt |
| 400 | Bad Request | Ongeldige input |
| 401 | Unauthorized | Geen authenticatie |
| 403 | Forbidden | Geen permissie |
| 404 | Not Found | Resource niet gevonden |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### **Error Response Format**
```json
{
  "error": {
    "code": "validation_error",
    "message": "Ongeldige invoer voor testimonial",
    "details": {
      "rating": ["Rating moet tussen 1 en 5 zijn."],
      "service": ["Dit veld is verplicht."]
    },
    "timestamp": "2024-01-15T10:00:00Z"
  }
}
```

## **Rate Limiting**

| Endpoint Type | Limiet | Periode |
|--------------|--------|---------|
| Publieke endpoints | 100 requests | Per minuut |
| Authenticated endpoints | 1000 requests | Per minuut |
| Admin endpoints | 5000 requests | Per minuut |
| Search endpoints | 50 requests | Per minuut |

## **Installatie & Configuratie**

### **Requirements**
```bash
# backend/requirements/base.txt
Django>=4.2
djangorestframework>=3.14
djongo>=1.3.6
pymongo>=4.3
djangorestframework-simplejwt>=5.3
python-decouple>=3.8
pillow>=10.0
django-filter>=23.3
corsheaders>=3.14
```

### **Environment Variables**
```env
# .env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=company_services
DB_HOST=localhost
DB_PORT=27017
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### **Database Setup**
```bash
# Migraties aanmaken
python manage.py makemigrations services

# Migraties uitvoeren
python manage.py migrate services

# Test data seeden
python manage.py shell
```

```python
# In Django shell - basis categorieën aanmaken
from services.models import ServiceCategory

categories = [
    ('Demontage & Montage', 'demontage_montage', 'fas fa-tools'),
    ('Möbel- & Elektroverkauf', 'mobel_verkauf', 'fas fa-couch'),
    ('Auto-Ankauf & -Verkauf', 'auto_ankauf', 'fas fa-car'),
    ('Autowerkstatt & Karosserie', 'autowerkstatt', 'fas fa-wrench'),
    ('Renovierung & Wiederaufbau', 'renovierung', 'fas fa-hammer'),
    ('Entsorgung', 'entsorgung', 'fas fa-trash-alt'),
    ('Transport & Verpackung', 'transport', 'fas fa-truck-moving'),
    ('Import & Export', 'import_export', 'fas fa-globe-europe'),
]

for name, category_type, icon in categories:
    ServiceCategory.objects.get_or_create(
        name=name,
        category_type=category_type,
        defaults={'icon': icon, 'show_on_homepage': True}
    )
```

## **Testing**

### **Unit Tests**
```bash
# Run service tests
python manage.py test services.tests

# Met coverage
coverage run --source='services' manage.py test services
coverage report
coverage html
```

### **API Tests**
```python
# Voorbeeld test
class ServiceAPITest(APITestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name='Test Categorie',
            slug='test-categorie',
            category_type='demontage_montage'
        )
    
    def test_service_list(self):
        response = self.client.get('/api/v1/services/services/')
        self.assertEqual(response.status_code, 200)
    
    def test_service_detail(self):
        service = Service.objects.create(
            name='Test Dienst',
            slug='test-dienst',
            category=self.category
        )
        response = self.client.get(f'/api/v1/services/services/{service.slug}/')
        self.assertEqual(response.status_code, 200)
```

## **Best Practices**

### **Code Organization**
```python
# services/
# ├── models.py           # Database modellen
# ├── serializers.py      # Data serializers
# ├── views.py           # API views
# ├── urls.py           # URL routing
# ├── permissions.py     # Custom permissions
# ├── filters.py        # Query filters
# ├── admin.py         # Admin interface
# └── signals.py       # Signal handlers
```

### **Naming Conventions**
- **Modellen**: PascalCase (Service, ServiceCategory)
- **Velden**: snake_case (has_fixed_price, display_order)
- **URLs**: kebab-case (/api/v1/services/)
- **Serializers**: ModelNameSerializer (ServiceSerializer)

### **Documentation Standards**
- Docstrings voor alle classes en methods
- Type hints waar mogelijk
- Commentaar voor complexe business logic
- API documentation met voorbeelden

## **Security Considerations**

### **Input Validation**
```python
# Model level validation
class Service(models.Model):
    fixed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

# Serializer level validation
class ServiceSerializer(serializers.ModelSerializer):
    def validate_fixed_price(self, value):
        if value and value <= 0:
            raise serializers.ValidationError("Prijs moet positief zijn.")
        return value
```

### **File Upload Security**
- Max file size: 10MB
- Allowed types: JPEG, PNG, WebP
- File name sanitization
- Virus scanning integration mogelijk

## **Monitoring & Analytics**

### **Tracking Metrics**
- **Service views**: Populariteit per dienst
- **Quote requests**: Lead generation tracking
- **Testimonial submissions**: Klanttevredenheid
- **Search queries**: Gebruikersinteresses

### **Admin Dashboard**
```python
# Statistics endpoint voor admin insights
/api/v1/services/statistics/

# Bevat:
# - Totaal aantal diensten
# - Actieve/Inactieve verdeling
# - Categorie statistieken
# - Populaire diensten
# - Maandelijkse trends
```

## **Troubleshooting**

### **Veelvoorkomende Problemen**

1. **Slug conflicten**
   ```bash
   # Controleer bestaande slugs
   python manage.py shell
   from services.models import Service
   Service.objects.filter(slug='keukenmontage').exists()
   ```

2. **Image upload errors**
   - Controleer MEDIA_ROOT permissions
   - Verify file size limits
   - Check supported image formats

3. **CORS errors**
   ```python
   # In settings.py
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",
       "http://127.0.0.1:3000",
   ]
   ```

4. **Database connection issues**
   ```bash
   # Test MongoDB connection
   mongo --host localhost --port 27017
   
   # Check Django database config
   python manage.py check --database default
   ```

## **Changelog**

### **Versie 1.0.0 (4 December 2025)**
- **Initial release** van Diensten API
- **8 vaste categorieën** volgens specificaties
- **Complete CRUD operations** voor alle modellen
- **Voor/Na portfolio systeem** voor renovatie diensten
- **Testimonial systeem** met moderation workflow
- **Service pakketten** met prijsopties
- **Geografische beschikbaarheid** (ServiceArea)
- **Analytics tracking** (views, quote requests)
- **Geavanceerde zoekfunctionaliteit**
- **Admin statistieken** dashboard

### **Versie 1.1.0 (Gepland)**
- **Real-time notifications** bij nieuwe testimonials
- **Export functionaliteit** voor service data
- **Bulk operations** voor service management
- **Advanced caching** met Redis
- **WebSocket support** voor live updates

## **Contact & Support**

### **Documentatie**
- **API Documentation**: `/api/v1/services/`
- **Admin Interface**: `/admin/services/`
- **GitHub Repository**: [link naar repo]
- **Swagger/OpenAPI**: `/swagger/` (optioneel)

### **Support Channels**
- **Email**: support@bedrijfsnaam.nl
- **Issue Tracker**: GitHub Issues
- **Documentatie Updates**: Regelmatige updates

### **Contributing**
1. Fork de repository
2. Maak een feature branch
3. Commit changes met duidelijke messages
4. Push naar de branch
5. Open een Pull Request

---

## **Bijlage: Vergelijking Producten vs Diensten API**

| Aspect | Producten API | Diensten API |
|--------|--------------|--------------|
| **Primair doel** | Verkoop van fysieke producten | Aanbieden van services |
| **Prijs model** | Vaste prijzen, kortingen | Vaste prijzen of offerte |
| **Voorraad** | Stock management | Geen voorraad (capacity based) |
| **Images** | Product foto's | Voor/Na portfolio |
| **Reviews** | Product beoordelingen | Dienst testimonials |
| **Packages** | N.v.t. | Service pakketten |
| **Availability** | Altijd beschikbaar | Per gebied (ServiceArea) |
| **Booking** | Directe aankoop | Online booking mogelijk |
| **SEO focus** | Product pagina's | Dienst landingspagina's |
| **Business logic** | Inventory, ordering | Appointment, quoting |

---

**Laatst bijgewerkt**: 4 December 2025  
**API Versie**: v1.0.0  
**Django Versie**: 4.2+  
**Database**: MongoDB via Djongo  
**Authenticatie**: JWT tokens  
**Documentatie Status**: Compleet

Deze API is ontworpen voor schaalbaarheid, prestaties en eenvoudige integratie met frontend applicaties. Voor vragen of suggesties, neem contact op met het developer AhmadAlDibo.
