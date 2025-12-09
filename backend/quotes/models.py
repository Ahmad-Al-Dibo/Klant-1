import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from decimal import Decimal
from core.models import TimeStampedModelWithSoftDelete


class QuoteStatus(models.TextChoices):
    """
    Status keuzes voor offertes.
    
    TECHNISCHE CONCEPTEN:
    - Django TextChoices voor type-safe enumerations
    - Status workflow management
    - Business process tracking
    """
    DRAFT = 'draft', _('Concept')
    PENDING = 'pending', _('In afwachting')
    SENT = 'sent', _('Verzonden')
    VIEWED = 'viewed', _('Bekeken')
    NEGOTIATION = 'negotiation', _('In onderhandeling')
    ACCEPTED = 'accepted', _('Geaccepteerd')
    REJECTED = 'rejected', _('Geweigerd')
    EXPIRED = 'expired', _('Verlopen')
    CANCELLED = 'cancelled', _('Geannuleerd')
    CONVERTED = 'converted', _('Omgezet naar order')


class QuotePriority(models.TextChoices):
    """
    Prioriteitsniveaus voor offertes.
    
    TECHNISCHE CONCEPTEN:
    - Priority-based routing
    - SLA compliance tracking
    """
    LOW = 'low', _('Laag')
    MEDIUM = 'medium', _('Medium')
    HIGH = 'high', _('Hoog')
    URGENT = 'urgent', _('Urgent')


class Quote(TimeStampedModelWithSoftDelete):
    """
    Hoofdmodel voor offertes.
    
    TECHNISCHE CONCEPTEN:
    - Complexe prijsberekeningen
    - Status workflow management
    - Multi-currency support
    - Validity period tracking
    - Version control voor revisies
    """
    
    # Identificatie en referentie
    quote_number = models.CharField(
        _('offerte nummer'),
        max_length=50,
        unique=True,
        editable=False,
        help_text=_('Uniek offertenummer gegenereerd door het systeem')
    )
    
    reference = models.CharField(
        _('referentie'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Interne referentie of klantreferentie')
    )
    
    revision = models.PositiveIntegerField(
        _('revisie'),
        default=1,
        help_text=_('Revisienummer van deze offerte')
    )
    
    parent_quote = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisions',
        verbose_name=_('originele offerte'),
        help_text=_('Originele offerte waarvan dit een revisie is')
    )
    
    # Klant informatie
    client = models.ForeignKey(
        'clients.Client',  # String referentie
        on_delete=models.PROTECT,
        related_name='quotes',
        verbose_name=_('klant'),
        help_text=_('Klant waarvoor de offerte is opgesteld')
    )
    
    contact_person = models.ForeignKey(
        'clients.ClientContact',  # String referentie
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes',
        verbose_name=_('contactpersoon'),
        help_text=_('Specifieke contactpersoon bij de klant')
    )
    
    # Status en workflow
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=QuoteStatus.choices,
        default=QuoteStatus.DRAFT,
        help_text=_('Huidige status van de offerte')
    )
    
    priority = models.CharField(
        _('prioriteit'),
        max_length=20,
        choices=QuotePriority.choices,
        default=QuotePriority.MEDIUM,
        help_text=_('Prioriteit voor behandeling')
    )
    
    # Prijs en valuta
    currency = models.CharField(
        _('valuta'),
        max_length=3,
        default='EUR',
        help_text=_('Valuta waarin de offerte is opgesteld (ISO 4217 code)')
    )
    
    exchange_rate = models.DecimalField(
        _('wisselkoers'),
        max_digits=10,
        decimal_places=6,
        default=1.0,
        help_text=_('Wisselkoers t.o.v. basisvaluta')
    )
    
    # Belastingen
    tax_rate = models.DecimalField(
        _('btw percentage'),
        max_digits=5,
        decimal_places=2,
        default=21.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('BTW percentage dat wordt toegepast')
    )
    
    tax_inclusive = models.BooleanField(
        _('btw inclusief'),
        default=True,
        help_text=_('Zijn de prijzen inclusief BTW?')
    )
    
    # Geldigheid
    valid_from = models.DateTimeField(
        _('geldig vanaf'),
        auto_now_add=True,
        help_text=_('Datum/tijd vanaf wanneer de offerte geldig is')
    )
    
    valid_until = models.DateTimeField(
        _('geldig tot'),
        help_text=_('Datum/tijd tot wanneer de offerte geldig is')
    )
    
    # Levering en betaling
    delivery_address = models.ForeignKey(
        'clients.Address',  # String referentie
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_quotes',
        verbose_name=_('afleveradres'),
        help_text=_('Afleveradres voor deze offerte')
    )
    
    billing_address = models.ForeignKey(
        'clients.Address',  # String referentie
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billing_quotes',
        verbose_name=_('factuuradres'),
        help_text=_('Factuuradres voor deze offerte')
    )

    delivery_date = models.DateTimeField(
        _('leverdatum'),
        null=True,
        blank=True,
        help_text=_('Gewenste leverdatum')
    )
    
    payment_terms = models.TextField(
        _('betalingsvoorwaarden'),
        blank=True,
        help_text=_('Specifieke betalingsvoorwaarden voor deze offerte')
    )
    
    delivery_terms = models.TextField(
        _('leveringsvoorwaarden'),
        blank=True,
        help_text=_('Specifieke leveringsvoorwaarden voor deze offerte')
    )
    
    # Notities en communicatie
    internal_notes = models.TextField(
        _('interne notities'),
        blank=True,
        help_text=_('Interne notities voor het team')
    )
    
    client_notes = models.TextField(
        _('klantnotities'),
        blank=True,
        help_text=_('Notities die op de offerte voor de klant verschijnen')
    )
    
    terms_conditions = models.TextField(
        _('algemene voorwaarden'),
        blank=True,
        help_text=_('Algemene voorwaarden van toepassing')
    )
    
    # Tracking
    sent_at = models.DateTimeField(
        _('verzonden op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer de offerte naar de klant is verzonden')
    )
    
    viewed_at = models.DateTimeField(
        _('bekeken op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer de klant de offerte heeft bekeken')
    )
    
    responded_at = models.DateTimeField(
        _('beantwoord op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd van klantreactie')
    )
    
    accepted_at = models.DateTimeField(
        _('geaccepteerd op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer de offerte is geaccepteerd')
    )
    
    expired_at = models.DateTimeField(
        _('verlopen op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer de offerte automatisch is verlopen')
    )
    
    # Conversie tracking
    converted_to_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_quote',
        verbose_name=_('omgezet naar order'),
        help_text=_('Order waar deze offerte naar is omgezet')
    )
    
    conversion_rate = models.FloatField(
        _('conversie percentage'),
        null=True,
        blank=True,
        help_text=_('Percentage van de totale waarde dat is geconverteerd')
    )
    
    # Metadata
    tags = models.ManyToManyField(
        'QuoteTag',
        blank=True,
        related_name='quotes',
        verbose_name=_('tags'),
        help_text=_('Tags voor categorisatie en filtering')
    )
    
    attachments = models.ManyToManyField(
        'QuoteAttachment',
        blank=True,
        related_name='quotes',
        verbose_name=_('bijlagen'),
        help_text=_('Documenten en bijlagen bij de offerte')
    )
    
    class Meta:
        verbose_name = _('offerte')
        verbose_name_plural = _('offertes')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['quote_number']),
            models.Index(fields=['status', 'valid_until']),
            models.Index(fields=['client', 'created_at']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['valid_until']),
            models.Index(fields=['sent_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(valid_until__gt=models.F('valid_from')),
                name='valid_until_after_valid_from'
            ),
        ]
    
    def __str__(self):
        return f"{self.quote_number} - {self.client}"
    
    def save(self, *args, **kwargs):
        """Auto-genereren van offertenummer bij aanmaak"""
        if not self.quote_number:
            self.quote_number = self.generate_quote_number()
        
        # Valideer geldigheidsperiode
        if self.valid_until and self.valid_until <= self.valid_from:
            from django.core.exceptions import ValidationError
            raise ValidationError(_('Geldig tot moet na geldig vanaf liggen'))
        
        # Auto-update status op basis van datums
        self.update_status_based_on_dates()
        
        super().save(*args, **kwargs)
    
    def generate_quote_number(self):
        """Genereer uniek offertenummer"""
        from django.utils import timezone
        import random
        import string
        
        year_month = timezone.now().strftime('%Y%m')
        sequential = Quote.objects.filter(
            quote_number__startswith=f'QT{year_month}'
        ).count() + 1
        
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"QT{year_month}{sequential:04d}{random_suffix}"
    
    def update_status_based_on_dates(self):
        """Update status automatisch op basis van geldigheidsdatum"""
        from django.utils import timezone
        
        if self.status not in [QuoteStatus.EXPIRED, QuoteStatus.CANCELLED, QuoteStatus.CONVERTED]:
            if self.valid_until and timezone.now() > self.valid_until:
                self.status = QuoteStatus.EXPIRED
                self.expired_at = timezone.now()
    
    @property
    def subtotal_excl_tax(self):
        """Totaalprijs exclusief BTW"""
        total = self.items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('quantity') * F('unit_price'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )['total'] or Decimal('0.00')
        
        # Als tax_inclusive, bereken exclusief
        if self.tax_inclusive:
            tax_factor = Decimal('1') + (self.tax_rate / Decimal('100'))
            return total / tax_factor
        return total
    
    @property
    def tax_amount(self):
        """BTW bedrag"""
        if self.tax_inclusive:
            tax_factor = Decimal('1') + (self.tax_rate / Decimal('100'))
            return self.subtotal_excl_tax * (self.tax_rate / Decimal('100'))
        else:
            return self.subtotal_excl_tax * (self.tax_rate / Decimal('100'))
    
    @property
    def total_incl_tax(self):
        """Totaalprijs inclusief BTW"""
        if self.tax_inclusive:
            return self.subtotal_excl_tax + self.tax_amount
        else:
            return self.subtotal_excl_tax * (Decimal('1') + (self.tax_rate / Decimal('100')))
    
    @property
    def discount_amount(self):
        """Totale korting bedrag"""
        return self.items.aggregate(
            total_discount=Sum(
                ExpressionWrapper(
                    F('quantity') * F('unit_price') * F('discount_percentage') / Decimal('100'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )['total_discount'] or Decimal('0.00')
    
    @property
    def profit_margin(self):
        """Winstmarge percentage"""
        total_cost = self.items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('quantity') * F('cost_price'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )['total'] or Decimal('0.00')
        
        if total_cost > 0:
            return ((self.subtotal_excl_tax - total_cost) / total_cost) * Decimal('100')
        return Decimal('0.00')
    
    @property
    def is_expired(self):
        """Is de offerte verlopen?"""
        from django.utils import timezone
        return self.valid_until and timezone.now() > self.valid_until
    
    @property
    def days_until_expiry(self):
        """Dagen tot vervaldatum"""
        from django.utils import timezone
        if self.valid_until:
            delta = self.valid_until - timezone.now()
            return delta.days
        return None
    
    @property
    def is_convertible(self):
        """Kan de offerte worden omgezet naar een order?"""
        return self.status == QuoteStatus.ACCEPTED and not self.converted_to_order
    
    def send_to_client(self):
        """Markeer offerte als verzonden"""
        from django.utils import timezone
        
        if self.status == QuoteStatus.DRAFT:
            self.status = QuoteStatus.SENT
            self.sent_at = timezone.now()
            self.save()
            # TODO: Trigger email notification
            return True
        return False
    
    def mark_as_viewed(self):
        """Markeer offerte als bekeken door klant"""
        from django.utils import timezone
        
        if self.status == QuoteStatus.SENT:
            self.status = QuoteStatus.VIEWED
            self.viewed_at = timezone.now()
            self.save()
            return True
        return False
    
    def accept(self):
        """Accepteer de offerte"""
        from django.utils import timezone
        
        if self.status in [QuoteStatus.SENT, QuoteStatus.VIEWED, QuoteStatus.NEGOTIATION]:
            self.status = QuoteStatus.ACCEPTED
            self.accepted_at = timezone.now()
            self.responded_at = timezone.now()
            self.save()
            # TODO: Trigger acceptance workflow
            return True
        return False
    
    def reject(self, reason=""):
        """Weiger de offerte"""
        from django.utils import timezone
        
        if self.status in [QuoteStatus.SENT, QuoteStatus.VIEWED, QuoteStatus.NEGOTIATION]:
            self.status = QuoteStatus.REJECTED
            self.responded_at = timezone.now()
            self.internal_notes = f"Afgewezen: {reason}\n{self.internal_notes}"
            self.save()
            # TODO: Trigger rejection workflow
            return True
        return False
    
    def create_revision(self):
        """Maak een nieuwe revisie van deze offerte"""
        # Clone the quote
        new_quote = Quote.objects.get(pk=self.pk)
        new_quote.pk = None
        new_quote.quote_number = None
        new_quote.parent_quote = self
        new_quote.revision = self.revision + 1
        new_quote.status = QuoteStatus.DRAFT
        new_quote.save()
        
        # Clone items
        for item in self.items.all():
            item.pk = None
            item.quote = new_quote
            item.save()
        
        return new_quote
    
    def convert_to_order(self):
        """Converteer offerte naar order"""
        if self.is_convertible:
            # TODO: Implement order creation logic
            # This would create an Order object from the quote
            pass
        return None


class QuoteItem(models.Model):
    """
    Items in een offerte.
    
    TECHNISCHE CONCEPTEN:
    - Line item management
    - Quantity and pricing calculations
    - Product/service linking
    """
    
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('offerte')
    )
    
    line_number = models.PositiveIntegerField(
        _('regelnummer'),
        default=1,
        help_text=_('Volgnummer in de offerte')
    )
    
    item_type = models.CharField(
        _('type item'),
        max_length=20,
        choices=[
            ('product', _('Product')),
            ('service', _('Dienst')),
            ('material', _('Materiaal')),
            ('labor', _('Arbeid')),
            ('other', _('Overig')),
        ],
        default='product',
        help_text=_('Type van dit item')
    )
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quote_items',
        verbose_name=_('product')
    )
    
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quote_items',
        verbose_name=_('dienst')
    )
    
    description = models.TextField(
        _('omschrijving'),
        help_text=_('Gedetailleerde omschrijving van het item')
    )
    
    specification = models.TextField(
        _('specificatie'),
        blank=True,
        help_text=_('Technische specificaties of aanvullende informatie')
    )
    
    quantity = models.DecimalField(
        _('aantal'),
        max_digits=10,
        decimal_places=3,
        default=1,
        validators=[MinValueValidator(0.001)],
        help_text=_('Aantal eenheden')
    )
    
    unit = models.CharField(
        _('eenheid'),
        max_length=20,
        default='stuk',
        help_text=_('Eenheid (stuk, uur, meter, etc.)')
    )
    
    unit_price = models.DecimalField(
        _('eenheidsprijs'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Prijs per eenheid exclusief BTW')
    )
    
    cost_price = models.DecimalField(
        _('kostprijs'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_('Kostprijs per eenheid (voor winstberekening)')
    )
    
    discount_percentage = models.DecimalField(
        _('kortingspercentage'),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Korting percentage op dit item')
    )
    
    tax_rate = models.DecimalField(
        _('btw percentage'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Specifiek BTW percentage voor dit item (laat leeg voor offerte default)')
    )
    
    delivery_week = models.PositiveIntegerField(
        _('leverweek'),
        null=True,
        blank=True,
        help_text=_('Geplande leverweek (optioneel)')
    )
    
    notes = models.TextField(
        _('notities'),
        blank=True,
        help_text=_('Interne notities over dit item')
    )
    
    class Meta:
        verbose_name = _('offerte item')
        verbose_name_plural = _('offerte items')
        ordering = ['line_number']
        unique_together = ['quote', 'line_number']
    
    def __str__(self):
        return f"{self.quote.quote_number} - Reg.{self.line_number}: {self.description[:50]}"
    
    @property
    def subtotal_excl_tax(self):
        """Subtotaal voor dit item exclusief BTW"""
        base = self.quantity * self.unit_price
        discount = base * (self.discount_percentage / Decimal('100'))
        return base - discount
    
    @property
    def tax_amount(self):
        """BTW bedrag voor dit item"""
        tax_rate = self.tax_rate if self.tax_rate is not None else self.quote.tax_rate
        return self.subtotal_excl_tax * (tax_rate / Decimal('100'))
    
    @property
    def total_incl_tax(self):
        """Totaal voor dit item inclusief BTW"""
        return self.subtotal_excl_tax + self.tax_amount
    
    @property
    def profit(self):
        """Winst op dit item"""
        if self.cost_price:
            return (self.unit_price - self.cost_price) * self.quantity
        return Decimal('0.00')
    
    @property
    def profit_margin(self):
        """Winstmarge percentage op dit item"""
        if self.cost_price and self.cost_price > 0:
            return ((self.unit_price - self.cost_price) / self.cost_price) * Decimal('100')
        return Decimal('0.00')
    
    def get_effective_tax_rate(self):
        """Effectief BTW percentage voor dit item"""
        return self.tax_rate if self.tax_rate is not None else self.quote.tax_rate


class QuoteTag(models.Model):
    """
    Tags voor categorisatie van offertes.
    
    TECHNISCHE CONCEPTEN:
    - Flexible categorization system
    - Color coding for visual identification
    """
    
    name = models.CharField(
        _('naam'),
        max_length=50,
        unique=True,
        help_text=_('Naam van de tag')
    )
    
    slug = models.SlugField(
        _('slug'),
        max_length=60,
        unique=True,
        help_text=_('URL-vriendelijke naam')
    )
    
    color = models.CharField(
        _('kleur'),
        max_length=7,
        default='#3498db',
        help_text=_('Hex kleurcode voor visualisatie')
    )
    
    description = models.TextField(
        _('beschrijving'),
        blank=True,
        help_text=_('Beschrijving van wanneer deze tag gebruikt wordt')
    )
    
    is_active = models.BooleanField(
        _('actief'),
        default=True,
        help_text=_('Of deze tag beschikbaar is voor gebruik')
    )
    
    class Meta:
        verbose_name = _('offerte tag')
        verbose_name_plural = _('offerte tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-genereren van slug"""
        from django.utils.text import slugify
        
        if not self.slug:
            self.slug = slugify(self.name)
        
        super().save(*args, **kwargs)


class QuoteAttachment(models.Model):
    """
    Bijlagen bij offertes.
    
    TECHNISCHE CONCEPTEN:
    - File upload management
    - Version control for documents
    - Access control
    """
    
    name = models.CharField(
        _('naam'),
        max_length=200,
        help_text=_('Beschrijvende naam van de bijlage')
    )
    
    file = models.FileField(
        _('bestand'),
        upload_to='quote_attachments/%Y/%m/%d/',
        help_text=_('Het geüploade bestand')
    )
    
    file_type = models.CharField(
        _('bestandstype'),
        max_length=100,
        blank=True,
        help_text=_('MIME type van het bestand')
    )
    
    file_size = models.PositiveIntegerField(
        _('bestandsgrootte'),
        blank=True,
        null=True,
        help_text=_('Grootte in bytes')
    )
    
    version = models.PositiveIntegerField(
        _('versie'),
        default=1,
        help_text=_('Versienummer van het document')
    )
    
    is_primary = models.BooleanField(
        _('hoofddocument'),
        default=False,
        help_text=_('Is dit het hoofdofferte document?')
    )
    
    uploaded_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='quote_attachments',
        verbose_name=_('geüpload door')
    )
    
    uploaded_at = models.DateTimeField(
        _('geüpload op'),
        auto_now_add=True
    )
    
    description = models.TextField(
        _('beschrijving'),
        blank=True,
        help_text=_('Extra beschrijving van de bijlage')
    )
    
    class Meta:
        verbose_name = _('offerte bijlage')
        verbose_name_plural = _('offerte bijlagen')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.name
    
    @property
    def file_extension(self):
        """Bestandsextensie"""
        if self.file.name:
            return self.file.name.split('.')[-1].lower()
        return ''
    
    @property
    def file_size_display(self):
        """Leesbare bestandsgrootte"""
        if self.file_size:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if self.file_size < 1024.0:
                    return f"{self.file_size:.1f} {unit}"
                self.file_size /= 1024.0
        return None


class QuoteTemplate(models.Model):
    """
    Herbruikbare templates voor offertes.
    
    TECHNISCHE CONCEPTEN:
    - Template-based quote generation
    - Standardized formatting
    - Placeholder system
    """
    
    name = models.CharField(
        _('naam'),
        max_length=200,
        unique=True,
        help_text=_('Naam van het template')
    )
    
    description = models.TextField(
        _('beschrijving'),
        blank=True,
        help_text=_('Beschrijving van wanneer dit template gebruikt wordt')
    )
    
    content = models.TextField(
        _('inhoud'),
        help_text=_('HTML/content template met placeholders')
    )
    
    header = models.TextField(
        _('koptekst'),
        blank=True,
        help_text=_('Template voor koptekst')
    )
    
    footer = models.TextField(
        _('voettekst'),
        blank=True,
        help_text=_('Template voor voettekst')
    )
    
    css_styles = models.TextField(
        _('CSS stijlen'),
        blank=True,
        help_text=_('Custom CSS voor opmaak')
    )
    
    default_tax_rate = models.DecimalField(
        _('standaard btw percentage'),
        max_digits=5,
        decimal_places=2,
        default=21.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    default_payment_terms = models.TextField(
        _('standaard betalingsvoorwaarden'),
        blank=True
    )
    
    default_validity_days = models.PositiveIntegerField(
        _('standaard geldigheidsduur (dagen)'),
        default=30,
        help_text=_('Standaard aantal dagen dat offerte geldig is')
    )
    
    is_active = models.BooleanField(
        _('actief'),
        default=True,
        help_text=_('Of dit template beschikbaar is voor gebruik')
    )
    
    created_at = models.DateTimeField(
        _('aangemaakt op'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('bijgewerkt op'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('offerte template')
        verbose_name_plural = _('offerte templates')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def create_quote_from_template(self, client, **kwargs):
        """Creëer een nieuwe offerte op basis van dit template"""
        from django.utils import timezone
        
        quote = Quote(
            client=client,
            tax_rate=self.default_tax_rate,
            payment_terms=self.default_payment_terms,
            valid_until=timezone.now() + timezone.timedelta(days=self.default_validity_days),
            **kwargs
        )
        
        quote.save()
        return quote


class QuoteHistory(models.Model):
    """
    Audit trail voor offerte wijzigingen.
    
    TECHNISCHE CONCEPTEN:
    - Change tracking
    - Version history
    - User action logging
    """
    
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('offerte')
    )
    
    action = models.CharField(
        _('actie'),
        max_length=50,
        choices=[
            ('created', _('Aangemaakt')),
            ('updated', _('Bijgewerkt')),
            ('status_changed', _('Status gewijzigd')),
            ('sent', _('Verzonden')),
            ('viewed', _('Bekeken')),
            ('accepted', _('Geaccepteerd')),
            ('rejected', _('Geweigerd')),
            ('converted', _('Omgezet')),
            ('revision', _('Revisie aangemaakt')),
        ]
    )
    
    old_value = models.TextField(
        _('oude waarde'),
        blank=True,
        null=True
    )
    
    new_value = models.TextField(
        _('nieuwe waarde'),
        blank=True,
        null=True
    )
    
    changed_fields = models.JSONField(
        _('gewijzigde velden'),
        default=list,
        help_text=_('Lijst van gewijzigde veldnamen')
    )
    
    changed_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='quote_changes',
        verbose_name=_('gewijzigd door')
    )
    
    changed_at = models.DateTimeField(
        _('gewijzigd op'),
        auto_now_add=True
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP adres'),
        blank=True,
        null=True
    )
    
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        _('notities'),
        blank=True,
        help_text=_('Extra informatie over de wijziging')
    )
    
    class Meta:
        verbose_name = _('offerte geschiedenis')
        verbose_name_plural = _('offerte geschiedenis')
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.quote.quote_number} - {self.action} op {self.changed_at}"
    

# quotes/models.py - QuoteDocument model
from django.db import models
from django.conf import settings
import os
import uuid


def quote_document_upload_path(instance, filename):
    """Generate upload path for quote documents"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"quotes/{instance.quote.quote_number}/documents/{filename}"


class QuoteDocument(models.Model):
    """Model for storing documents related to quotes"""
    
    DOCUMENT_TYPES = [
        ('quote', 'Quote'),
        ('contract', 'Contract'),
        ('attachment', 'Attachment'),
        ('other', 'Other'),
    ]
    
    quote = models.ForeignKey(
        'Quote', 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=20, 
        choices=DOCUMENT_TYPES, 
        default='attachment'
    )
    file = models.FileField(
        upload_to=quote_document_upload_path,
        max_length=255
    )
    notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_documents'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_documents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Quote Document"
        verbose_name_plural = "Quote Documents"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {os.path.basename(self.file.name)}"
    
    def delete(self, *args, **kwargs):
        """Delete file when document is deleted"""
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)
    
    @property
    def file_exists(self):
        """Check if file exists on storage"""
        return self.file and os.path.exists(self.file.path)
    
    @property
    def mime_type(self):
        """Get MIME type based on file extension"""
        ext = os.path.splitext(self.file.name)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.txt': 'text/plain',
        }
        return mime_types.get(ext, 'application/octet-stream')