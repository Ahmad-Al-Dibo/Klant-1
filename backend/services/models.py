from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class ServiceCategory(models.Model):
    """
    Hoofdcategorieën voor diensten volgens specificaties
    """
    CATEGORY_CHOICES = [
        ('demontage_montage', _('Demontage & Montage')),
        ('mobel_verkauf', _('Möbel- & Elektroverkauf')),
        ('auto_ankauf', _('Auto-Ankauf & -Verkauf')),
        ('autowerkstatt', _('Autowerkstatt & Karosserie')),
        ('renovierung', _('Renovierung & Wiederaufbau')),
        ('entsorgung', _('Entsorgung')),
        ('transport', _('Transport & Verpackung')),
        ('import_export', _('Import & Export')),
    ]
    
    name = models.CharField(_('categorie naam'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    category_type = models.CharField(_('categorie type'), max_length=50, 
                                     choices=CATEGORY_CHOICES, unique=True)
    icon = models.CharField(_('icoon'), max_length=50, blank=True,
                           help_text=_('Font Awesome icon class, bijv.: fas fa-tools'))
    description = models.TextField(_('beschrijving'))
    image = models.ImageField(_('categorie afbeelding'), upload_to='service_categories/', 
                             blank=True, null=True)
    
    # Volgorde en zichtbaarheid
    display_order = models.PositiveIntegerField(_('weergave volgorde'), default=0)
    is_active = models.BooleanField(_('actief'), default=True)
    show_on_homepage = models.BooleanField(_('toon op homepage'), default=False)
    
    # SEO
    meta_title = models.CharField(_('meta titel'), max_length=200, blank=True)
    meta_description = models.TextField(_('meta beschrijving'), blank=True)
    meta_keywords = models.TextField(_('meta keywords'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('dienst categorie')
        verbose_name_plural = _('dienst categorieën')
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('service-category-detail', kwargs={'slug': self.slug})
    
    @property
    def service_count(self):
        return self.services.filter(is_active=True).count()


class Service(models.Model):
    """
    Individuele diensten binnen een categorie
    """
    name = models.CharField(_('dienst naam'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, 
                                related_name='services', verbose_name=_('categorie'))
    
    # Beschrijving
    short_description = models.TextField(_('korte beschrijving'), max_length=500)
    full_description = models.TextField(_('volledige beschrijving'))
    benefits = models.TextField(_('voordelen'), blank=True,
                               help_text=_('Lijst van voordelen (gebruik bullets)'))
    process = models.TextField(_('werkwijze'), blank=True,
                              help_text=_('Beschrijving van de werkwijze'))
    
    # Prijzen en tijden
    has_fixed_price = models.BooleanField(_('vaste prijs'), default=False)
    fixed_price = models.DecimalField(_('vaste prijs'), max_digits=10, decimal_places=2,
                                     blank=True, null=True, validators=[MinValueValidator(0)])
    price_description = models.CharField(_('prijs beschrijving'), max_length=200, blank=True,
                                        help_text=_('Bijv: "Vanaf €50" of "Op aanvraag"'))
    estimated_time = models.CharField(_('geschatte tijd'), max_length=100, blank=True,
                                     help_text=_('Bijv: "2-4 uur" of "1 dag"'))
    
    # Kenmerken
    is_popular = models.BooleanField(_('populaire dienst'), default=False)
    is_featured = models.BooleanField(_('uitgelicht'), default=False)
    is_active = models.BooleanField(_('actief'), default=True)
    
    # Vereisten
    requirements = models.TextField(_('vereisten'), blank=True,
                                   help_text=_('Wat heeft de klant nodig?'))
    
    # Service details
    requires_quote = models.BooleanField(_('offerte nodig'), default=True)
    can_book_online = models.BooleanField(_('online boekbaar'), default=False)
    has_emergency_service = models.BooleanField(_('spoedservice'), default=False)
    
    # SEO
    meta_title = models.CharField(_('meta titel'), max_length=200, blank=True)
    meta_description = models.TextField(_('meta beschrijving'), blank=True)
    meta_keywords = models.TextField(_('meta keywords'), blank=True)
    
    # Statistieken
    views_count = models.PositiveIntegerField(_('aantal bekeken'), default=0)
    quote_requests_count = models.PositiveIntegerField(_('aantal offerte aanvragen'), default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(_('gepubliceerd op'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('dienst')
        verbose_name_plural = _('diensten')
        ordering = ['category__display_order', 'name']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_popular', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.category.name}: {self.name}"
    
    def get_absolute_url(self):
        return reverse('service-detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Verhoog het aantal views"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_quote_requests(self):
        """Verhoog het aantal offerte aanvragen"""
        self.quote_requests_count += 1
        self.save(update_fields=['quote_requests_count'])


class ServiceImage(models.Model):
    """
    Afbeeldingen voor diensten (voor/na, portfolio)
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('afbeelding'), upload_to='services/%Y/%m/%d/')
    caption = models.CharField(_('bijschrift'), max_length=200, blank=True)
    alt_text = models.CharField(_('alternatieve tekst'), max_length=200, blank=True)
    
    # Voor/na functionaliteit
    is_before_image = models.BooleanField(_('voor afbeelding'), default=False)
    is_after_image = models.BooleanField(_('na afbeelding'), default=False)
    
    # Weergave
    display_order = models.PositiveIntegerField(_('weergave volgorde'), default=0)
    is_primary = models.BooleanField(_('hoofdafbeelding'), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('dienst afbeelding')
        verbose_name_plural = _('dienst afbeeldingen')
        ordering = ['display_order', '-is_primary', 'created_at']
    
    def __str__(self):
        return f"Afbeelding voor {self.service.name}"


class FAQ(models.Model):
    """
    Veelgestelde vragen per dienst
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(_('vraag'), max_length=500)
    answer = models.TextField(_('antwoord'))
    display_order = models.PositiveIntegerField(_('weergave volgorde'), default=0)
    is_active = models.BooleanField(_('actief'), default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['display_order', 'created_at']
    
    def __str__(self):
        return self.question


class ServiceFeature(models.Model):
    """
    Kenmerken/voordelen van diensten
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(_('titel'), max_length=100)
    description = models.TextField(_('beschrijving'), blank=True)
    icon = models.CharField(_('icoon'), max_length=50, blank=True,
                           help_text=_('Font Awesome icon class'))
    display_order = models.PositiveIntegerField(_('weergave volgorde'), default=0)
    
    class Meta:
        verbose_name = _('dienst kenmerk')
        verbose_name_plural = _('dienst kenmerken')
        ordering = ['display_order']
    
    def __str__(self):
        return self.title


class ServicePackage(models.Model):
    """
    Pakketten/bundels voor diensten
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(_('pakket naam'), max_length=100)
    description = models.TextField(_('beschrijving'))
    price = models.DecimalField(_('prijs'), max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(0)])
    duration = models.CharField(_('duur'), max_length=100, blank=True,
                               help_text=_('Bijv: "3 uur" of "1 dag"'))
    
    # Inclusief/exclusief
    includes = models.TextField(_('inclusief'), blank=True,
                               help_text=_('Wat is inbegrepen (lijst)'))
    excludes = models.TextField(_('exclusief'), blank=True,
                               help_text=_('Wat is niet inbegrepen (lijst)'))
    
    is_popular = models.BooleanField(_('populair pakket'), default=False)
    display_order = models.PositiveIntegerField(_('weergave volgorde'), default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('dienst pakket')
        verbose_name_plural = _('dienst pakketten')
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.service.name} - {self.name}"


class ServiceArea(models.Model):
    """
 Gebieden waar de dienst beschikbaar is
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='areas')
    city = models.CharField(_('stad'), max_length=100)
    postal_code = models.CharField(_('postcode'), max_length=10, blank=True)
    region = models.CharField(_('regio'), max_length=100, blank=True)
    is_active = models.BooleanField(_('actief'), default=True)
    
    class Meta:
        verbose_name = _('dienst gebied')
        verbose_name_plural = _('dienst gebieden')
        unique_together = ['service', 'city', 'postal_code']
    
    def __str__(self):
        return f"{self.service.name} - {self.city}"


class Testimonial(models.Model):
    """
    Klantbeoordelingen voor diensten
    """
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, 
                               related_name='testimonials', verbose_name=_('dienst'))
    client_name = models.CharField(_('klant naam'), max_length=100)
    client_location = models.CharField(_('locatie klant'), max_length=100, blank=True)
    client_company = models.CharField(_('bedrijf klant'), max_length=100, blank=True)
    
    content = models.TextField(_('beoordeling'))
    rating = models.PositiveIntegerField(_('beoordeling'), choices=RATING_CHOICES)
    
    # Goedkeuring en weergave
    is_approved = models.BooleanField(_('goedgekeurd'), default=False)
    is_featured = models.BooleanField(_('uitgelicht'), default=False)
    display_order = models.PositiveIntegerField(_('weergave volgorde'), default=0)
    
    # Project referentie
    project_date = models.DateField(_('project datum'), blank=True, null=True)
    project_description = models.CharField(_('project beschrijving'), max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('testimonial')
        verbose_name_plural = _('testimonials')
        ordering = ['-is_featured', 'display_order', '-created_at']
    
    def __str__(self):
        return f"Testimonial van {self.client_name} voor {self.service.name}"
    
    @property
    def rating_stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)


class ServiceView(models.Model):
    """
    Tracking van dienstweergaven voor analytics
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='view_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                            null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('dienst weergave')
        verbose_name_plural = _('dienst weergaven')
        indexes = [
            models.Index(fields=['service', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Weergave van {self.service.name} op {self.created_at}"