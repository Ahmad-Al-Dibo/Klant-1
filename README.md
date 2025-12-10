# **System API Documentatie**

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

# **Projecten API Documentatie**

## **Overzicht**

De Projecten API biedt een complete oplossing voor projectmanagement en -tracking. Deze API ondersteunt alle functionaliteit voor het beheren van projecten met een focus op technische implementatie, resource planning en voortgangsbewaking. Het systeem is speciaal ontwikkeld voor het beheren van projecten binnen technische en constructie-industrieën.

## **Project Management Concepten**

### **Kern Functionaliteiten**
- **Project planning**: Tijdlijn management met milestones
- **Resource allocation**: Team toewijzing en capacity planning
- **Budget tracking**: Kosten monitoring en budget controle
- **Progress monitoring**: Voortgangsbewaking en KPI tracking
- **Document management**: Project documentatie en versiebeheer

### **Project Workflows**
1. **Concept** → **Planning** → **Actief** → **Voltooid**
2. **Prioriteit management**: Laag → Medium → Hoog → Urgent
3. **Team collaboration**: Multi-user project assignment
4. **Timeline tracking**: Gepland vs werkelijke tijdlijnen

## **API Endpoints**

### **Project Categorieën**

#### **Lijst van project categorieën**
```
GET /api/v1/projects/categories/
```

**Parameters:**
- `active_only` (optioneel): Toon alleen actieve categorieën
- `search` (optioneel): Zoek op naam of beschrijving

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Technische Installatie",
      "slug": "technische-installatie",
      "description": "Projecten voor technische installaties",
      "icon": "fas fa-cogs",
      "color": "#3498db",
      "color_display": "<span style='background-color: #3498db;'></span>",
      "is_active": true,
      "project_count": 12,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **Categorie detail**
```
GET /api/v1/projects/categories/{slug}/
```

#### **Projecten in categorie**
```
GET /api/v1/projects/categories/{slug}/projects/
```

### **Project Tags**

#### **Lijst van project tags**
```
GET /api/v1/projects/tags/
```

**Parameters:**
- `active_only` (optioneel): Toon alleen actieve tags
- `search` (optioneel): Zoek op naam

**Response:**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Urgent",
      "slug": "urgent",
      "color": "#e74c3c",
      "color_display": "<span style='background-color: #e74c3c;'></span>",
      "description": "Projecten die dringend aandacht nodig hebben",
      "is_active": true,
      "project_count": 3,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### **Projecten**

#### **Project lijst**
```
GET /api/v1/projects/projects/
```

**Query Parameters:**
- `search`: Zoek in projectnummer, naam, beschrijving
- `status`: Filter op status (draft, planning, active, on_hold, completed, cancelled, archived)
- `priority`: Filter op prioriteit (low, medium, high, urgent)
- `category`: Filter op categorie slug
- `project_manager`: Filter op project manager ID
- `client`: Filter op klant naam
- `start_date_after`: Startdatum na
- `start_date_before`: Startdatum voor
- `end_date_after`: Einddatum na
- `end_date_before`: Einddatum voor
- `has_budget`: Filter op projecten met budget > 0
- `overdue`: Toon alleen achterstallige projecten
- `active_only`: Toon alleen actieve projecten
- `ordering`: Sorteer op veld (- voor descending)
- `page`: Pagina nummer
- `page_size`: Items per pagina

**Beschikbare ordering velden:**
- `project_number`, `name`, `status`, `priority`, `start_date`, `end_date`, `budget`, `created_at`

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/projects/projects/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "project_number": "PRJ2410001AB",
      "name": "Keuken Renovatie Project",
      "description": "Complete renovatie van restaurant keuken",
      "status": "active",
      "status_display": "Actief",
      "priority": "high",
      "priority_display": "Hoog",
      "client": "Restaurant De Ster",
      "contact_person": "Peter de Vries",
      "project_manager": {
        "id": 3,
        "full_name": "Jan Smit",
        "email": "jan@bedrijf.nl"
      },
      "team_members": [
        {
          "id": 4,
          "full_name": "Lisa Jansen",
          "role": "Technicus"
        },
        {
          "id": 5,
          "full_name": "Mark de Wit",
          "role": "Installateur"
        }
      ],
      "start_date": "2024-01-10",
      "end_date": "2024-03-15",
      "actual_start_date": "2024-01-12",
      "actual_end_date": null,
      "duration_days": 65,
      "actual_duration_days": null,
      "budget": "15000.00",
      "currency": "EUR",
      "progress_percentage": 45,
      "total_costs": "6500.00",
      "budget_utilization": 43.33,
      "is_active": true,
      "is_overdue": false,
      "category": {
        "id": 1,
        "name": "Renovatie",
        "slug": "renovatie"
      },
      "tags": [
        {
          "id": 2,
          "name": "Renovatie",
          "slug": "renovatie",
          "color": "#2ecc71"
        },
        {
          "id": 3,
          "name": "Hoog Budget",
          "slug": "hoog-budget",
          "color": "#f39c12"
        }
      ],
      "created_at": "2024-01-05T09:30:00Z",
      "updated_at": "2024-01-20T14:15:00Z"
    }
  ]
}
```

#### **Project detail**
```
GET /api/v1/projects/projects/{project_number}/
```

**Response:**
```json
{
  "id": 1,
  "project_number": "PRJ2410001AB",
  "name": "Keuken Renovatie Project",
  "description": "Complete renovatie van restaurant keuken inclusief alle technische installaties...",
  "status": "active",
  "status_display": "Actief",
  "priority": "high",
  "priority_display": "Hoog",
  "client": "Restaurant De Ster",
  "contact_person": "Peter de Vries",
  "project_manager": {
    "id": 3,
    "full_name": "Jan Smit",
    "email": "jan@bedrijf.nl",
    "phone": "+31 6 12345678",
    "role": "Senior Project Manager"
  },
  "team_members": [
    {
      "id": 4,
      "full_name": "Lisa Jansen",
      "email": "lisa@bedrijf.nl",
      "phone": "+31 6 23456789",
      "role": "Technicus"
    },
    {
      "id": 5,
      "full_name": "Mark de Wit",
      "email": "mark@bedrijf.nl",
      "phone": "+31 6 34567890",
      "role": "Installateur"
    }
  ],
  "start_date": "2024-01-10",
  "end_date": "2024-03-15",
  "actual_start_date": "2024-01-12",
  "actual_end_date": null,
  "duration_days": 65,
  "actual_duration_days": null,
  "budget": "15000.00",
  "currency": "EUR",
  "progress_percentage": 45,
  "total_costs": "6500.00",
  "budget_utilization": 43.33,
  "is_active": true,
  "is_overdue": false,
  "internal_notes": "Klant heeft specifieke eisen voor ventilatiesysteem...",
  "client_notes": "Werkzaamheden alleen uitvoeren buiten openingstijden.",
  "requirements": "1. NEN3140 certificering vereist\n2. Alle materialen moeten voedselveilig zijn\n3. Werk volgens HACCP normen",
  "category": {
    "id": 1,
    "name": "Renovatie",
    "slug": "renovatie",
    "icon": "fas fa-hammer",
    "color": "#3498db"
  },
  "tags": [
    {
      "id": 2,
      "name": "Renovatie",
      "slug": "renovatie",
      "color": "#2ecc71",
      "description": "Renovatie projecten"
    }
  ],
  "completed_at": null,
  "cancelled_at": null,
  "created_at": "2024-01-05T09:30:00Z",
  "updated_at": "2024-01-20T14:15:00Z",
  "deleted_at": null,
  "timeline_status": {
    "planned_duration": 65,
    "actual_duration": 54,
    "days_behind": -2,
    "completion_rate": 45,
    "critical_path": ["Installatie ventilatie", "Elektra aanpassingen"]
  },
  "financial_status": {
    "budget_allocated": "15000.00",
    "costs_incurred": "6500.00",
    "remaining_budget": "8500.00",
    "cost_variance": "-500.00",
    "forecast_completion": "14250.00"
  },
  "resource_status": {
    "team_size": 3,
    "total_hours_planned": 320,
    "total_hours_logged": 145,
    "utilization_rate": 45.31
  }
}
```

#### **Project aanmaken**
```
POST /api/v1/projects/projects/
```

**Request Body:**
```json
{
  "name": "Nieuw Technisch Project",
  "description": "Beschrijving van het nieuwe project",
  "status": "draft",
  "priority": "medium",
  "client": "Nieuwe Klant BV",
  "contact_person": "John Doe",
  "project_manager": 3,
  "team_members": [4, 5, 6],
  "start_date": "2024-02-01",
  "end_date": "2024-05-31",
  "budget": "20000.00",
  "currency": "EUR",
  "category": 1,
  "tags": [2, 3],
  "requirements": "Project specifieke vereisten..."
}
```

#### **Project bijwerken**
```
PUT /api/v1/projects/projects/{project_number}/
PATCH /api/v1/projects/projects/{project_number}/
```

#### **Project verwijderen (soft delete)**
```
DELETE /api/v1/projects/projects/{project_number}/
```

#### **Project herstellen**
```
POST /api/v1/projects/projects/{project_number}/restore/
```

### **Project Voortgang**

#### **Project voortgang bijwerken**
```
POST /api/v1/projects/projects/{project_number}/update-progress/
```

**Request Body:**
```json
{
  "status": "active",
  "actual_start_date": "2024-01-12",
  "progress_notes": "Alle voorbereidingen zijn afgerond, gestart met installatie.",
  "cost_update": {
    "amount": "1500.00",
    "description": "Materialen aankoop week 3"
  }
}
```

#### **Project voltooien**
```
POST /api/v1/projects/projects/{project_number}/complete/
```

**Request Body:**
```json
{
  "actual_end_date": "2024-03-10",
  "completion_notes": "Project succesvol afgerond, klant tevreden.",
  "final_costs": "14250.00"
}
```

#### **Project annuleren**
```
POST /api/v1/projects/projects/{project_number}/cancel/
```

**Request Body:**
```json
{
  "cancellation_reason": "Klant heeft project geannuleerd wegens budget redenen.",
  "cancelled_at": "2024-02-15T10:00:00Z"
}
```

### **Team Management**

#### **Team lid toevoegen aan project**
```
POST /api/v1/projects/projects/{project_number}/add-team-member/
```

**Request Body:**
```json
{
  "user_id": 7,
  "role": "Technisch Adviseur",
  "hours_allocated": 40
}
```

#### **Team lid verwijderen van project**
```
POST /api/v1/projects/projects/{project_number}/remove-team-member/
```

**Request Body:**
```json
{
  "user_id": 5
}
```

#### **Team allocation bijwerken**
```
PUT /api/v1/projects/projects/{project_number}/team-allocation/
```

**Request Body:**
```json
{
  "allocations": [
    {"user_id": 4, "hours_per_week": 20},
    {"user_id": 5, "hours_per_week": 25},
    {"user_id": 6, "hours_per_week": 15}
  ]
}
```

### **Budget Management**

#### **Budget bijwerken**
```
POST /api/v1/projects/projects/{project_number}/update-budget/
```

**Request Body:**
```json
{
  "new_budget": "17500.00",
  "reason": "Extra werkzaamheden geïdentificeerd",
  "approved_by": 2
}
```

#### **Kosten toevoegen**
```
POST /api/v1/projects/projects/{project_number}/add-cost/
```

**Request Body:**
```json
{
  "amount": "1200.50",
  "description": "Aankoop speciaal gereedschap",
  "category": "materialen",
  "date_incurred": "2024-01-22",
  "invoice_number": "INV-2024-00123"
}
```

#### **Kosten overzicht**
```
GET /api/v1/projects/projects/{project_number}/costs/
```

**Response:**
```json
{
  "total_costs": "6500.00",
  "budget_remaining": "8500.00",
  "budget_utilization_percentage": 43.33,
  "costs_by_category": {
    "materialen": "3500.00",
    "arbeid": "2500.00",
    "diensten": "500.00"
  },
  "recent_costs": [
    {
      "id": 1,
      "amount": "1200.50",
      "description": "Aankoop speciaal gereedschap",
      "category": "materialen",
      "date_incurred": "2024-01-22",
      "invoice_number": "INV-2024-00123",
      "added_by": {
        "id": 3,
        "full_name": "Jan Smit"
      },
      "created_at": "2024-01-22T11:30:00Z"
    }
  ]
}
```

### **Project Zoeken**

#### **Geavanceerd zoeken**
```
GET /api/v1/projects/search/
```

**Parameters:**
- `q`: Zoekterm
- `status`: Status filter
- `priority`: Prioriteit filter
- `category`: Categorie slug
- `project_manager`: Project manager ID
- `has_budget`: Boolean filter
- `start_date_range`: Startdatum range (YYYY-MM-DD,YYYY-MM-DD)
- `end_date_range`: Einddatum range (YYYY-MM-DD,YYYY-MM-DD)
- `min_budget`: Minimum budget
- `max_budget`: Maximum budget
- `overdue_only`: Toon alleen achterstallige
- `sort_by`: Sorteer op (newest, oldest, budget_high, budget_low, priority, name)
- `page`: Pagina nummer
- `page_size`: Items per pagina

**Response:**
```json
{
  "count": 15,
  "results": [...],
  "search_params": {
    "q": "renovatie",
    "status": "active",
    "min_budget": "10000",
    "sort_by": "priority"
  },
  "aggregations": {
    "by_status": {
      "active": 8,
      "planning": 4,
      "completed": 3
    },
    "by_priority": {
      "high": 5,
      "medium": 7,
      "low": 3
    }
  }
}
```

### **Project Statistieken**

#### **Overzicht statistieken**
```
GET /api/v1/projects/statistics/
```

**Parameters:**
- `period`: Periode (today, week, month, quarter, year)
- `category`: Filter op categorie
- `project_manager`: Filter op project manager

**Response:**
```json
{
  "summary": {
    "total_projects": 45,
    "active_projects": 18,
    "completed_projects": 22,
    "cancelled_projects": 5,
    "total_budget": "450000.00",
    "total_costs": "285000.00",
    "average_completion_rate": 78.5
  },
  "status_distribution": {
    "draft": 3,
    "planning": 8,
    "active": 18,
    "on_hold": 2,
    "completed": 22,
    "cancelled": 5,
    "archived": 7
  },
  "priority_distribution": {
    "low": 12,
    "medium": 20,
    "high": 10,
    "urgent": 3
  },
  "category_stats": [
    {
      "name": "Renovatie",
      "project_count": 15,
      "total_budget": "175000.00",
      "average_completion_rate": 82.3
    },
    {
      "name": "Installatie",
      "project_count": 12,
      "total_budget": "120000.00",
      "average_completion_rate": 75.6
    }
  ],
  "budget_utilization": {
    "under_budget": 28,
    "on_budget": 12,
    "over_budget": 5
  },
  "timeline_performance": {
    "on_schedule": 30,
    "slightly_behind": 10,
    "significantly_behind": 5
  },
  "recent_activity": {
    "projects_created": 3,
    "projects_completed": 2,
    "projects_updated": 15
  }
}
```

#### **Project manager statistieken**
```
GET /api/v1/projects/statistics/managers/
```

**Response:**
```json
{
  "managers": [
    {
      "id": 3,
      "full_name": "Jan Smit",
      "total_projects": 12,
      "active_projects": 5,
      "completed_projects": 7,
      "completion_rate": 92.5,
      "average_budget_utilization": 87.3,
      "on_time_delivery_rate": 85.0
    }
  ],
  "top_performers": [...],
  "performance_trends": [...]
}
```

### **Project Export**

#### **Projecten exporteren als CSV**
```
GET /api/v1/projects/export/csv/
```

**Parameters:**
- `status`: Status filter
- `start_date_after`: Startdatum filter
- `end_date_before`: Einddatum filter
- `columns`: Kolommen om te exporteren (comma separated)

**Response:** CSV file download

#### **Projecten exporteren als PDF rapport**
```
GET /api/v1/projects/export/pdf/{project_number}/
```

#### **Project Gantt chart data**
```
GET /api/v1/projects/{project_number}/gantt-data/
```

**Response:**
```json
{
  "project": {
    "name": "Keuken Renovatie Project",
    "start_date": "2024-01-10",
    "end_date": "2024-03-15"
  },
  "tasks": [
    {
      "id": 1,
      "name": "Voorbereiding",
      "start_date": "2024-01-10",
      "end_date": "2024-01-17",
      "progress": 100,
      "dependencies": "",
      "resource": "Jan Smit"
    },
    {
      "id": 2,
      "name": "Demontage oude keuken",
      "start_date": "2024-01-15",
      "end_date": "2024-01-22",
      "progress": 100,
      "dependencies": "1",
      "resource": "Installatie team"
    }
  ]
}
```

## **Data Modellen**

### **Project**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| project_number | String | Uniek projectnummer (auto-generated) |
| name | String | Project naam |
| description | Text | Gedetailleerde beschrijving |
| status | String | Status (draft, planning, active, on_hold, completed, cancelled, archived) |
| priority | String | Prioriteit (low, medium, high, urgent) |
| client | Text | Klant naam (tijdelijk TextField) |
| contact_person | Text | Contactpersoon bij klant |
| project_manager | ForeignKey | Project manager (User model) |
| team_members | ManyToMany | Team leden (User model) |
| start_date | Date | Geplande startdatum |
| end_date | Date | Geplande einddatum |
| actual_start_date | Date | Werkelijke startdatum |
| actual_end_date | Date | Werkelijke einddatum |
| budget | Decimal | Totaal budget |
| currency | String | Valuta code (default: EUR) |
| internal_notes | Text | Interne notities |
| client_notes | Text | Notities voor klant |
| requirements | Text | Projectvereisten en specificaties |
| category | ForeignKey | Project categorie |
| tags | ManyToMany | Project tags |
| completed_at | DateTime | Voltooiingsdatum/tijd |
| cancelled_at | DateTime | Annuleringsdatum/tijd |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |
| deleted_at | DateTime | Soft delete datum |

### **ProjectCategory**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| name | String | Categorie naam |
| slug | String | URL-vriendelijke naam |
| description | Text | Beschrijving |
| icon | String | FontAwesome icon class |
| color | String | Hex kleurcode |
| is_active | Boolean | Is categorie actief? |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |

### **ProjectTag**
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| name | String | Tag naam |
| slug | String | URL-vriendelijke naam |
| color | String | Hex kleurcode |
| description | Text | Beschrijving |
| is_active | Boolean | Is tag actief? |
| created_at | DateTime | Aanmaakdatum |
| updated_at | DateTime | Update datum |

### **ProjectCost** (Optioneel voor toekomstige uitbreiding)
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| project | ForeignKey | Gerelateerd project |
| amount | Decimal | Kosten bedrag |
| description | String | Kosten beschrijving |
| category | String | Kosten categorie |
| date_incurred | Date | Datum kosten gemaakt |
| invoice_number | String | Factuurnummer |
| approved_by | ForeignKey | Goedgekeurd door |
| created_at | DateTime | Aanmaakdatum |

### **ProjectTask** (Optioneel voor toekomstige uitbreiding)
| Veld | Type | Beschrijving |
|------|------|-------------|
| id | Integer | Unieke identifier |
| project | ForeignKey | Gerelateerd project |
| name | String | Taak naam |
| description | Text | Taak beschrijving |
| status | String | Taak status |
| assigned_to | ForeignKey | Toegewezen aan |
| due_date | Date | Deadline |
| completed_at | DateTime | Voltooiingsdatum |
| created_at | DateTime | Aanmaakdatum |

## **Project Status Flow**

### **Status Transities**
```
Concept (DRAFT) → In planning (PLANNING) → Actief (ACTIVE)
    ↓               ↓                     ↓
Gearchiveerd    Gepauzeerd            Voltooid (COMPLETED)
(ARCHIVED)      (ON_HOLD)            ↗
                                    ↗
Geannuleerd (CANCELLED) ←─────────┘
```

### **Status Beschrijvingen**
| Status | Omschrijving | Toegestane acties |
|--------|-------------|-------------------|
| **DRAFT** | Concept fase | Bewerken, Verwijderen, Verplaatsen naar PLANNING |
| **PLANNING** | In planning fase | Team toewijzen, Budget instellen, Planning maken, Verplaatsen naar ACTIVE |
| **ACTIVE** | Actief project | Voortgang bijwerken, Kosten registreren, Team aanpassen, Pauzeren (ON_HOLD), Voltooien (COMPLETED), Annuleren (CANCELLED) |
| **ON_HOLD** | Gepauzeerd | Heractiveren (ACTIVE), Annuleren (CANCELLED) |
| **COMPLETED** | Voltooid | Archiveren (ARCHIVED) |
| **CANCELLED** | Geannuleerd | Archiveren (ARCHIVED) |
| **ARCHIVED** | Gearchiveerd | Alleen bekijken (read-only) |

### **Priority Levels**
| Prioriteit | Beschrijving | Response Time | Escalatie Pad |
|------------|-------------|---------------|---------------|
| **LOW** | Laag - Geen tijdsdruk | Binnen 2 weken | Project Manager |
| **MEDIUM** | Medium - Normale planning | Binnen 1 week | Project Manager |
| **HIGH** | Hoog - Dringend | Binnen 48 uur | Hoofd Project Management |
| **URGENT** | Urgent - Onmiddellijk | Binnen 24 uur | Directie |

## **Business Rules & Validaties**

### **Project Number Generation**
```python
# Format: PRJ + jaar + sequentieel nummer + random suffix
# Voorbeeld: PRJ2410001AB
def generate_project_number():
    year = timezone.now().strftime("%y")  # 24 voor 2024
    sequential = Project.objects.filter(
        project_number__startswith=f"PRJ{year}"
    ).count() + 1
    random_suffix = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"PRJ{year}{sequential:04d}{random_suffix}"
```

### **Budget Validaties**
- Budget mag niet negatief zijn
- Kosten mogen budget niet overschrijden (waarschuwing bij >90%)
- Valuta conversie ondersteuning voor multi-currency projecten

### **Timeline Validaties**
- Startdatum mag niet na einddatum liggen
- Werkelijke startdatum mag niet voor geplande startdatum liggen (kan later zijn)
- Project kan niet voltooid worden zonder werkelijke einddatum

### **Team Validaties**
- Project manager moet actieve gebruiker zijn
- Team members moeten actieve gebruikers zijn
- Gebruiker kan niet aan meer dan X gelijktijdige projecten werken (configurable)

## **API Authenticatie & Permissies**

### **JWT Token Authenticatie**
```bash
# Token verkrijgen
POST /api/auth/token/
{
  "email": "gebruiker@bedrijf.nl",
  "password": "wachtwoord"
}

# Token refresh
POST /api/auth/token/refresh/
{
  "refresh": "refresh-token-here"
}

# Authenticatie Header
Authorization: Bearer <access_token>
```

### **Permission Levels**
| Rol | Permissies | Endpoints |
|-----|------------|-----------|
| **Super Admin** | Volledige toegang | Alle endpoints |
| **Project Manager** | Eigen projecten + team | Project CRUD, Team management, Budget beheer |
| **Team Member** | Toegewezen projecten | Project lezen, Voortgang bijwerken, Taken beheren |
| **Klant** | Alleen eigen projecten | Project status lezen, Notities toevoegen |
| **Public** | Geen toegang | Alleen publieke statistieken (indien beschikbaar) |

### **Endpoint Permissies Overzicht**
| Endpoint | Admin | Project Manager | Team Member | Klant |
|----------|-------|----------------|-------------|-------|
| GET /projects/ | ✓ | ✓ (eigen) | ✓ (toegewezen) | ✓ (eigen) |
| POST /projects/ | ✓ | ✓ | ✗ | ✗ |
| PUT/PATCH /projects/{id}/ | ✓ | ✓ (eigen) | ✗ | ✗ |
| DELETE /projects/{id}/ | ✓ | ✗ | ✗ | ✗ |
| POST /projects/{id}/complete/ | ✓ | ✓ (eigen) | ✗ | ✗ |
| POST /projects/{id}/add-team-member/ | ✓ | ✓ (eigen) | ✗ | ✗ |
| GET /statistics/ | ✓ | ✓ (eigen) | ✗ | ✗ |
| GET /export/csv/ | ✓ | ✓ (eigen) | ✗ | ✗ |

## **Integratie Voorbeelden**

### **Frontend Integratie**
```javascript
// Project lijst ophalen
fetch('/api/v1/projects/projects/?status=active&ordering=-priority', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
.then(response => response.json())
.then(data => {
  console.log(data.results);
});

// Nieuw project aanmaken
fetch('/api/v1/projects/projects/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    name: 'Nieuw Renovatie Project',
    description: 'Beschrijving...',
    status: 'planning',
    priority: 'high',
    client: 'Klant Naam',
    budget: '25000.00'
  })
});

// Voortgang bijwerken
fetch('/api/v1/projects/projects/PRJ2410001AB/update-progress/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    status: 'active',
    progress_notes: 'Gestart met fase 2'
  })
});
```

### **Webhook Notificaties**
```python
# Project status change webhook
WEBHOOK_EVENTS = {
    'project.created',
    'project.updated',
    'project.completed',
    'project.cancelled',
    'project.overdue',
    'budget.exceeded'
}

# Webhook payload voorbeeld
{
  "event": "project.completed",
  "project": {
    "project_number": "PRJ2410001AB",
    "name": "Keuken Renovatie Project",
    "status": "completed",
    "actual_end_date": "2024-03-10"
  },
  "timestamp": "2024-03-10T15:30:00Z",
  "user": {
    "id": 3,
    "name": "Jan Smit"
  }
}
```

## **Dashboard Widgets**

### **Project Overview Widget**
```json
{
  "widget_type": "project_overview",
  "data": {
    "total_projects": 45,
    "active_projects": 18,
    "overdue_projects": 3,
    "total_budget": "450000.00",
    "budget_utilization": "63.33%"
  },
  "trend": {
    "projects_created_this_month": 5,
    "projects_completed_this_month": 3,
    "change_vs_last_month": "+12%"
  }
}
```

### **Project Status Distribution Widget**
```json
{
  "widget_type": "status_distribution",
  "data": {
    "labels": ["Actief", "In planning", "Voltooid", "Gepauzeerd", "Geannuleerd"],
    "datasets": [{
      "data": [18, 8, 22, 2, 5],
      "backgroundColor": ["#28a745", "#17a2b8", "#007bff", "#ffc107", "#dc3545"]
    }]
  }
}
```

### **Upcoming Deadlines Widget**
```json
{
  "widget_type": "upcoming_deadlines",
  "data": [
    {
      "project_number": "PRJ2410001AB",
      "name": "Keuken Renovatie",
      "end_date": "2024-03-15",
      "days_remaining": 5,
      "status": "active",
      "priority": "high"
    },
    {
      "project_number": "PRJ2410002CD",
      "name": "Elektra Installatie",
      "end_date": "2024-03-20",
      "days_remaining": 10,
      "status": "active",
      "priority": "medium"
    }
  ]
}
```

## **SEO & Metadata**

### **Automatische SEO Velden**
- **Project URLs**: `/projects/PRJ2410001AB/`
- **Meta titel**: `{project_name} - {company_name}`
- **Meta beschrijving**: Korte project beschrijving (max 160 chars)
- **Structured data**: Schema.org Project markup

### **Sitemap Integratie**
```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://bedrijf.nl/projects/PRJ2410001AB/</loc>
    <lastmod>2024-01-20T14:15:00Z</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

## **Performance Optimalisatie**

### **Query Optimization**
```python
# Gebruik select_related en prefetch_related
projects = Project.objects.select_related(
    'project_manager',
    'category'
).prefetch_related(
    'team_members',
    'tags'
).filter(
    deleted_at__isnull=True
).only(
    'project_number',
    'name',
    'status',
    'priority',
    'start_date',
    'end_date'
)
```

### **Caching Strategie**
```python
# Cache project lijst voor 15 minuten
@method_decorator(cache_page(60 * 15))
def list(self, request):
    return super().list(request)

# Cache project detail voor 5 minuten
@method_decorator(cache_page(60 * 5))
def retrieve(self, request, *args, **kwargs):
    return super().retrieve(request, *args, **kwargs)

# Cache statistieken voor 1 uur
@method_decorator(cache_page(60 * 60))
def statistics(self, request):
    # ...
```

### **Pagination Settings**
```python
# Default pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Large datasets gebruiken cursor pagination
class ProjectViewSet(viewsets.ModelViewSet):
    pagination_class = CursorPagination
    ordering = '-created_at'
```

## **Error Handling**

### **HTTP Status Codes**
| Code | Beschrijving | Voorbeeld |
|------|-------------|-----------|
| 200 | OK | Succesvolle GET request |
| 201 | Created | Project succesvol aangemaakt |
| 400 | Bad Request | Ongeldige input data |
| 401 | Unauthorized | Geen of ongeldige authenticatie |
| 403 | Forbidden | Geen toegang tot resource |
| 404 | Not Found | Project niet gevonden |
| 409 | Conflict | Projectnummer bestaat al |
| 422 | Unprocessable Entity | Business rule violation |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### **Error Response Format**
```json
{
  "error": {
    "code": "project_validation_error",
    "message": "Project validatie gefaald",
    "details": {
      "budget": ["Budget mag niet negatief zijn."],
      "end_date": ["Einddatum moet na startdatum liggen."]
    },
    "timestamp": "2024-01-15T10:00:00Z",
    "request_id": "req_1234567890abcdef"
  }
}
```

### **Custom Error Codes**
| Code | Omschrijving | Oplossing |
|------|-------------|-----------|
| `project_not_found` | Project bestaat niet | Controleer projectnummer |
| `invalid_status_transition` | Ongeldige status wijziging | Volg status flow diagram |
| `budget_exceeded` | Kosten overschrijden budget | Pas budget aan of verminder kosten |
| `team_member_overloaded` | Team lid heeft te veel projecten | Verdeel werk anders |
| `project_overdue` | Project is achter op schema | Pas planning aan |

## **Rate Limiting**

| Gebruikerstype | Limiet | Periode | Endpoints |
|----------------|--------|---------|-----------|
| Anonymous | 10 requests | Per minuut | Alleen GET /public/ |
| Authenticated | 100 requests | Per minuut | Alle niet-admin endpoints |
| Project Manager | 500 requests | Per minuut | Alle manager endpoints |
| Admin | 1000 requests | Per minuut | Alle endpoints |

## **Testing**

### **Test Data Setup**
```python
# tests/factories.py
class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
    
    project_number = factory.Sequence(lambda n: f"PRJ24{n:04d}AB")
    name = factory.Faker('sentence', nb_words=4)
    status = "draft"
    priority = "medium"
    client = factory.Faker('company')
    budget = Decimal('10000.00')
```

### **API Tests**
```python
# tests/test_api.py
class ProjectAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@bedrijf.nl',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_project(self):
        data = {
            'name': 'Test Project',
            'description': 'Test beschrijving',
            'status': 'draft',
            'priority': 'medium',
            'client': 'Test Klant',
            'budget': '5000.00'
        }
        response = self.client.post('/api/v1/projects/projects/', data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('project_number', response.data)
    
    def test_project_list_filtering(self):
        response = self.client.get('/api/v1/projects/projects/?status=active')
        self.assertEqual(response.status_code, 200)
    
    def test_project_completion(self):
        project = ProjectFactory(status='active')
        response = self.client.post(
            f'/api/v1/projects/projects/{project.project_number}/complete/',
            {'actual_end_date': '2024-01-31'}
        )
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertEqual(project.status, 'completed')
```

### **Integration Tests**
```python
# tests/test_integration.py
class ProjectWorkflowTest(APITestCase):
    def test_complete_project_workflow(self):
        # 1. Create project
        # 2. Move to planning
        # 3. Assign team
        # 4. Update progress
        # 5. Complete project
        # Verify all steps and final state
        pass
```

## **Monitoring & Analytics**

### **Key Performance Indicators (KPIs)**
1. **Project Success Rate**: % projecten tijdig en binnen budget voltooid
2. **Budget Utilization**: Gemiddeld budget gebruik percentage
3. **Team Utilization**: Gemiddelde bezettingsgraad teamleden
4. **Client Satisfaction**: Gemiddelde klantbeoordeling
5. **On-Time Delivery**: % projecten op tijd voltooid

### **Dashboard Metrics**
```json
{
  "metrics": {
    "project_health": {
      "excellent": 15,
      "good": 20,
      "warning": 7,
      "critical": 3
    },
    "financial_performance": {
      "under_budget": 28,
      "on_budget": 12,
      "over_budget": 5,
      "average_over_budget": "8.5%"
    },
    "resource_utilization": {
      "optimal": 65,
      "under_utilized": 20,
      "over_utilized": 15,
      "average_utilization": "72%"
    }
  }
}
```

## **Security Considerations**

### **Data Protection**
- **GDPR compliance**: Klantgegevens versleuteld
- **Access control**: Role-based permissions
- **Audit logging**: Alle wijzigingen gelogd
- **Data retention**: Projecten automatisch archiveren na X jaar

### **Input Validation**
```python
class ProjectSerializer(serializers.ModelSerializer):
    def validate_budget(self, value):
        if value < 0:
            raise serializers.ValidationError("Budget mag niet negatief zijn.")
        return value
    
    def validate_end_date(self, value):
        if self.initial_data.get('start_date'):
            start_date = parse_date(self.initial_data['start_date'])
            if value < start_date:
                raise serializers.ValidationError(
                    "Einddatum moet na startdatum liggen."
                )
        return value
```

### **API Security Headers**
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## **Migration & Deployment**

### **Database Migraties**
```bash
# Maak migraties aan
python manage.py makemigrations projects

# Voer migraties uit
python manage.py migrate projects

# Rollback indien nodig
python manage.py migrate projects 0001_initial
```

### **Production Deployment Checklist**
1. ✅ Environment variables geconfigureerd
2. ✅ Database backups ingesteld
3. ✅ SSL/TLS certificaten geïnstalleerd
4. ✅ Rate limiting geconfigureerd
5. ✅ Monitoring alerts ingesteld
6. ✅ Disaster recovery plan getest
7. ✅ Load balancing geconfigureerd
8. ✅ Caching strategy geïmplementeerd

### **Backup & Restore**
```bash
# Database backup
mongodump --db company_services --out /backups/

# Restore backup
mongorestore --db company_services /backups/company_services/

# Media files backup
rsync -avz media/ backup-server:/backups/media/
```

## **Troubleshooting**

### **Veelvoorkomende Problemen**

1. **Projectnummer generatie faalt**
   ```bash
   # Controleer MongoDB connectie
   python manage.py shell
   from projects.models import Project
   print(Project.objects.count())
   ```

2. **Permission denied errors**
   ```python
   # Controleer user permissions
   user.has_perm('projects.add_project')
   user.has_perm('projects.change_project')
   ```

3. **Budget overschrijding waarschuwingen**
   - Controleer kosten registraties
   - Pas budget aan indien nodig
   - Genereer overbudget rapport

4. **Team allocation conflicts**
   ```python
   # Controleer beschikbaarheid teamlid
   user.projects.filter(status='active').count()
   # Maximaal 5 actieve projecten per gebruiker
   ```

### **Debug Logging**
```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'projects_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/projects_api.log',
        },
    },
    'loggers': {
        'projects': {
            'handlers': ['projects_file'],
            'level': 'DEBUG',
        },
    },
}
```

## **Changelog**

### **Versie 1.0.0 (12 December 2025)**
- Initial release van Projecten API
- Complete project management functionaliteit
- Team allocation en resource planning
- Budget tracking en kostenbeheer
- Geavanceerde zoek- en filter mogelijkheden
- Real-time statistieken en rapportages
- Multi-user collaboratie
- Soft delete functionaliteit
- JWT authenticatie integratie
- Role-based permissions systeem


## **Support & Contact**

### **Support Channels**
- **Email**: ahmadaldibo212009@gmail.com
- **Telefoon**: +31 686020505


### **SLA (Service Level Agreement)**
- **Availability**: 99.9% uptime
- **Response Time**: < 100ms voor 95% van requests
- **Support Hours**: 24/7 voor kritieke issues
- **Backup Frequency**: Dagelijks volledig, elk uur incrementeel

---

*Laatst bijgewerkt: 12 December 2025*  
*API Versie: v1.0.0*  
*Contact: ahmadaldibo212009@gmail.com*
