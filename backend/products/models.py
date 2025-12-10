from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class ProductCategory(models.Model):
    """
    Categorieën voor producten (bijv. Meubels, Elektronica, Antiek)
    """
    name = models.CharField(_('categorie naam'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('beschrijving'), blank=True)
    image = models.ImageField(_('categorie afbeelding'), upload_to='product_categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')
    is_active = models.BooleanField(_('actief'), default=True)
    display_order = models.PositiveIntegerField(_('weergave volgorde'), default=0)
    
    # Metadata
    meta_title = models.CharField(_('meta titel'), max_length=200, blank=True)
    meta_description = models.TextField(_('meta beschrijving'), blank=True)
    meta_keywords = models.TextField(_('meta keywords'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('product categorie')
        verbose_name_plural = _('product categorieën')
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_all_products_count(self):
        """Totaal aantal producten in categorie (inclusief subcategorieën)"""
        return Product.objects.filter(categories__in=self.get_descendants(include_self=True)).count()
    
    def get_descendants(self, include_self=False):
        """Haal alle subcategorieën op"""
        descendants = []
        if include_self:
            descendants.append(self)
        
        for subcategory in self.subcategories.all():
            descendants.append(subcategory)
            descendants.extend(subcategory.get_descendants())
        
        return descendants


class Product(models.Model):
    """
    Product model voor meubels, elektrische apparaten en antiek
    """
    CONDITION_CHOICES = [
        ('new', _('Nieuw')),
        ('like_new', _('Zo goed als nieuw')),
        ('good', _('Goed')),
        ('fair', _('Redelijk')),
        ('refurbished', _('Gerenoveerd')),
    ]
    
    STATUS_CHOICES = [
        ('available', _('Beschikbaar')),
        ('sold', _('Verkocht')),
        ('reserved', _('Gereserveerd')),
        ('pending', _('In afwachting')),
    ]
    
    # Basis informatie
    title = models.CharField(_('product titel'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    short_description = models.TextField(_('korte beschrijving'), max_length=500)
    full_description = models.TextField(_('volledige beschrijving'))
    
    # Categorisatie
    categories = models.ManyToManyField(ProductCategory, related_name='products', verbose_name=_('categorieën'))
    
    # Prijs informatie
    price = models.DecimalField(_('prijs'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    original_price = models.DecimalField(_('originele prijs'), max_digits=10, decimal_places=2, 
                                         blank=True, null=True, validators=[MinValueValidator(0)])
    is_on_sale = models.BooleanField(_('in de aanbieding'), default=False)
    sale_price = models.DecimalField(_('aanbiedingsprijs'), max_digits=10, decimal_places=2,
                                    blank=True, null=True, validators=[MinValueValidator(0)])
    
    # Voorraad en conditie
    sku = models.CharField(_('SKU'), max_length=100, unique=True, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(_('voorraad hoeveelheid'), default=1)
    low_stock_threshold = models.PositiveIntegerField(_('lage voorraad drempel'), default=5)
    condition = models.CharField(_('conditie'), max_length=20, choices=CONDITION_CHOICES, default='good')
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Specificaties
    brand = models.CharField(_('merk'), max_length=100, blank=True)
    model = models.CharField(_('model'), max_length=100, blank=True)
    dimensions = models.CharField(_('afmetingen'), max_length=100, blank=True, 
                                 help_text=_('Bijv: 120x80x60 cm'))
    weight = models.DecimalField(_('gewicht'), max_digits=8, decimal_places=2, blank=True, null=True,
                                help_text=_('In kilogram'))
    material = models.CharField(_('materiaal'), max_length=100, blank=True)
    color = models.CharField(_('kleur'), max_length=50, blank=True)
    
    # Verkoop informatie
    is_featured = models.BooleanField(_('uitgelicht'), default=False)
    is_bestseller = models.BooleanField(_('bestseller'), default=False)
    views_count = models.PositiveIntegerField(_('aantal bekeken'), default=0)
    
    # Levering informatie
    requires_assembly = models.BooleanField(_('montage nodig'), default=False)
    assembly_service_available = models.BooleanField(_('montageservice beschikbaar'), default=True)
    delivery_available = models.BooleanField(_('bezorging beschikbaar'), default=True)
    
    # SEO
    meta_title = models.CharField(_('meta titel'), max_length=200, blank=True)
    meta_description = models.TextField(_('meta beschrijving'), blank=True)
    meta_keywords = models.TextField(_('meta keywords'), blank=True)
    
    # Audit velden
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, related_name='created_products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(_('gepubliceerd op'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('producten')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        """Is het product actief en beschikbaar?"""
        return self.status == 'available' and self.stock_quantity > 0
    
    @property
    def final_price(self):
        """Bepaal de uiteindelijke prijs (rekening houdend met aanbiedingen)"""
        if self.is_on_sale and self.sale_price:
            return self.sale_price
        return self.price
    
    @property
    def discount_percentage(self):
        """Bereken kortingspercentage"""
        if self.is_on_sale and self.sale_price and self.original_price:
            discount = ((self.original_price - self.sale_price) / self.original_price) * 100
            return round(discount, 2)
        return 0
    
    def increment_views(self):
        """Verhoog het aantal views"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def decrease_stock(self, quantity=1):
        """Verminder voorraad"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            if self.stock_quantity == 0:
                self.status = 'sold'
            self.save(update_fields=['stock_quantity', 'status'])
            return True
        return False
    
    def is_low_stock(self):
        """Controleer of voorraad laag is"""
        return self.stock_quantity <= self.low_stock_threshold


class ProductImage(models.Model):
    """
    Afbeeldingen voor producten
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('afbeelding'), upload_to='products/%Y/%m/%d/')
    alt_text = models.CharField(_('alternatieve tekst'), max_length=200, blank=True)
    caption = models.CharField(_('bijschrift'), max_length=200, blank=True)
    display_order = models.PositiveIntegerField(_('weergave volgorde'), default=0)
    is_primary = models.BooleanField(_('hoofdafbeelding'), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('product afbeelding')
        verbose_name_plural = _('product afbeeldingen')
        ordering = ['display_order', '-is_primary', 'created_at']
    
    def __str__(self):
        return f"Afbeelding voor {self.product.title}"


class ProductFeature(models.Model):
    """
    Kenmerken/specificaties van producten
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(_('kenmerk naam'), max_length=100)
    value = models.CharField(_('waarde'), max_length=200)
    icon = models.CharField(_('icoon'), max_length=50, blank=True, 
                           help_text=_('Font Awesome icon class, bijv.: fas fa-check'))
    display_order = models.PositiveIntegerField(_('weergave volgorde'), default=0)
    
    class Meta:
        verbose_name = _('product kenmerk')
        verbose_name_plural = _('product kenmerken')
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.name}: {self.value}"


class ProductReview(models.Model):
    """
    Beoordelingen van producten door klanten
    """
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                            null=True, blank=True, related_name='product_reviews')
    
    # Review details
    rating = models.PositiveIntegerField(_('beoordeling'), choices=RATING_CHOICES)
    title = models.CharField(_('titel'), max_length=200, blank=True)
    comment = models.TextField(_('opmerking'))
    
    # Reviewer info (voor niet-ingelogde gebruikers)
    reviewer_name = models.CharField(_('naam beoordelaar'), max_length=100, blank=True)
    reviewer_email = models.EmailField(_('email beoordelaar'), blank=True)
    
    # Moderation
    is_approved = models.BooleanField(_('goedgekeurd'), default=False)
    is_verified_purchase = models.BooleanField(_('geverifieerde aankoop'), default=False)
    
    helpful_yes = models.PositiveIntegerField(_('handig - ja'), default=0)
    helpful_no = models.PositiveIntegerField(_('handig - nee'), default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('product beoordeling')
        verbose_name_plural = _('product beoordelingen')
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"Beoordeling voor {self.product.title} door {self.reviewer_name or self.user}"
    
    @property
    def helpful_score(self):
        """Bereken handigheidsscore"""
        total = self.helpful_yes + self.helpful_no
        if total > 0:
            return (self.helpful_yes / total) * 100
        return 0


class ProductView(models.Model):
    """
    Bijhouden van productweergaven voor analytics
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='view_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('product weergave')
        verbose_name_plural = _('product weergaven')
        indexes = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Weergave van {self.product.title} op {self.created_at}"