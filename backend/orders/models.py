import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from decimal import Decimal
from core.models import TimeStampedModelWithSoftDelete


class OrderStatus(models.TextChoices):
    """
    Status keuzes voor orders.
    
    TECHNISCHE CONCEPTEN:
    - Django TextChoices voor type-safe enumerations
    - Order workflow management
    - Business process tracking
    """
    DRAFT = 'draft', _('Concept')
    PENDING = 'pending', _('In afwachting')
    CONFIRMED = 'confirmed', _('Bevestigd')
    PROCESSING = 'processing', _('In verwerking')
    READY_FOR_SHIPMENT = 'ready_for_shipment', _('Gereed voor verzending')
    SHIPPED = 'shipped', _('Verzonden')
    DELIVERED = 'delivered', _('Afgeleverd')
    PARTIALLY_DELIVERED = 'partially_delivered', _('Gedeeltelijk afgeleverd')
    CANCELLED = 'cancelled', _('Geannuleerd')
    REFUNDED = 'refunded', _('Terugbetaald')
    COMPLETED = 'completed', _('Voltooid')


class OrderPriority(models.TextChoices):
    """
    Prioriteitsniveaus voor orders.
    
    TECHNISCHE CONCEPTEN:
    - Priority-based processing
    - SLA compliance tracking
    """
    LOW = 'low', _('Laag')
    MEDIUM = 'medium', _('Medium')
    HIGH = 'high', _('Hoog')
    URGENT = 'urgent', _('Urgent')


class PaymentStatus(models.TextChoices):
    """
    Betaalstatus voor orders.
    
    TECHNISCHE CONCEPTEN:
    - Payment workflow management
    - Financial tracking
    """
    PENDING = 'pending', _('In afwachting')
    PARTIALLY_PAID = 'partially_paid', _('Gedeeltelijk betaald')
    PAID = 'paid', _('Betaald')
    OVERDUE = 'overdue', _('Achterstallig')
    REFUNDED = 'refunded', _('Terugbetaald')
    FAILED = 'failed', _('Mislukt')


class Order(TimeStampedModelWithSoftDelete):
    """
    Hoofdmodel voor orders.
    
    TECHNISCHE CONCEPTEN:
    - Complexe order management
    - Status workflow management
    - Multi-currency support
    - Payment tracking
    - Shipping and delivery management
    """
    
    # Identificatie en referentie
    order_number = models.CharField(
        _('ordernummer'),
        max_length=50,
        unique=True,
        editable=False,
        help_text=_('Uniek ordernummer gegenereerd door het systeem')
    )
    
    reference = models.CharField(
        _('referentie'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Interne referentie of klantreferentie')
    )
    
    # Relaties
    quote = models.ForeignKey(
        'quotes.Quote',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('offerte'),
        help_text=_('Offerte waarvan deze order is gemaakt'),
    )
    
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_('klant'),
        help_text=_('Klant voor wie de order is')
    )
    
    contact_person = models.ForeignKey(
        'clients.ClientContact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('contactpersoon'),
        help_text=_('Contactpersoon bij de klant')
    )
    
    # Status en workflow
    status = models.CharField(
        _('status'),
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.DRAFT,
        help_text=_('Huidige status van de order')
    )
    
    priority = models.CharField(
        _('prioriteit'),
        max_length=20,
        choices=OrderPriority.choices,
        default=OrderPriority.MEDIUM,
        help_text=_('Prioriteit voor verwerking')
    )
    
    # Prijs en valuta
    currency = models.CharField(
        _('valuta'),
        max_length=3,
        default='EUR',
        help_text=_('Valuta waarin de order is opgesteld (ISO 4217 code)')
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
    
    # Betaling
    payment_status = models.CharField(
        _('betaalstatus'),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text=_('Huidige betaalstatus')
    )
    
    payment_method = models.CharField(
        _('betaalmethode'),
        max_length=50,
        choices=[
            ('bank_transfer', _('Bankoverschrijving')),
            ('credit_card', _('Creditcard')),
            ('debit_card', _('Debitcard')),
            ('paypal', _('PayPal')),
            ('ideal', _('iDEAL')),
            ('cash', _('Contant')),
            ('invoice', _('Factuur')),
            ('other', _('Overig')),
        ],
        default='invoice',
        help_text=_('Gebruikte betaalmethode')
    )
    
    payment_terms = models.TextField(
        _('betalingsvoorwaarden'),
        blank=True,
        help_text=_('Specifieke betalingsvoorwaarden voor deze order')
    )
    
    payment_due_date = models.DateField(
        _('vervaldatum betaling'),
        null=True,
        blank=True,
        help_text=_('Datum waarop betaling vervalt')
    )
    
    # Levering
    delivery_address = models.ForeignKey(
        'clients.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_orders',
        verbose_name=_('afleveradres'),
        help_text=_('Afleveradres voor deze order')
    )
    
    billing_address = models.ForeignKey(
        'clients.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billing_orders',
        verbose_name=_('factuuradres'),
        help_text=_('Factuuradres voor deze order')
    )
    
    delivery_date = models.DateTimeField(
        _('leverdatum'),
        null=True,
        blank=True,
        help_text=_('Geplande leverdatum')
    )
    
    actual_delivery_date = models.DateTimeField(
        _('werkelijke leverdatum'),
        null=True,
        blank=True,
        help_text=_('Werkelijke leverdatum')
    )
    
    shipping_method = models.CharField(
        _('verzendmethode'),
        max_length=100,
        blank=True,
        help_text=_('Gebruikte verzendmethode')
    )
    
    tracking_number = models.CharField(
        _('trackingnummer'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Trackingnummer voor verzending')
    )
    
    shipping_costs = models.DecimalField(
        _('verzendkosten'),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Kosten voor verzending')
    )
    
    # Notities en voorwaarden
    internal_notes = models.TextField(
        _('interne notities'),
        blank=True,
        help_text=_('Interne notities voor het team')
    )
    
    client_notes = models.TextField(
        _('klantnotities'),
        blank=True,
        help_text=_('Notities voor de klant')
    )
    
    terms_conditions = models.TextField(
        _('algemene voorwaarden'),
        blank=True,
        help_text=_('Algemene voorwaarden van toepassing')
    )
    
    delivery_instructions = models.TextField(
        _('leveringsinstructies'),
        blank=True,
        help_text=_('Speciale instructies voor levering')
    )
    
    # Tracking
    confirmed_at = models.DateTimeField(
        _('bevestigd op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer de order is bevestigd')
    )
    
    processing_started_at = models.DateTimeField(
        _('verwerking gestart op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer verwerking is gestart')
    )
    
    shipped_at = models.DateTimeField(
        _('verzonden op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer de order is verzonden')
    )
    
    delivered_at = models.DateTimeField(
        _('afgeleverd op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer de order is afgeleverd')
    )
    
    cancelled_at = models.DateTimeField(
        _('geannuleerd op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer de order is geannuleerd')
    )
    
    completed_at = models.DateTimeField(
        _('voltooid op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer de order is voltooid')
    )
    
    # Project relatie (optioneel)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('project'),
        help_text=_('Project waartoe deze order behoort')
    )
    
    # Metadata
    tags = models.ManyToManyField(
        'OrderTag',
        blank=True,
        related_name='orders',
        verbose_name=_('tags'),
        help_text=_('Tags voor categorisatie en filtering')
    )
    
    attachments = models.ManyToManyField(
        'OrderAttachment',
        blank=True,
        related_name='orders',
        verbose_name=_('bijlagen'),
        help_text=_('Documenten en bijlagen bij de order')
    )
    
    assigned_to = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        verbose_name=_('toegewezen aan'),
        help_text=_('Medewerker verantwoordelijk voor deze order')
    )
    
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['client', 'created_at']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['delivery_date']),
            models.Index(fields=['assigned_to', 'status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(delivery_date__gt=models.F('created_at')),
                name='delivery_date_after_creation'
            ),
        ]
    
    def __str__(self):
        return f"{self.order_number} - {self.client}"
    
    def save(self, *args, **kwargs):
        """Auto-genereren van ordernummer bij aanmaak"""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # Auto-set delivery_date als niet opgegeven
        if not self.delivery_date and self.quote and self.quote.delivery_date:
            self.delivery_date = self.quote.delivery_date
        
        # Auto-set payment_due_date op basis van betalingsvoorwaarden
        if not self.payment_due_date and self.payment_terms:
            from django.utils import timezone
            import re
            
            # Parse betalingsvoorwaarden voor dagen
            days_match = re.search(r'(\d+)\s*dagen', self.payment_terms)
            if days_match:
                days = int(days_match.group(1))
                self.payment_due_date = timezone.now().date() + timezone.timedelta(days=days)
        
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Genereer uniek ordernummer"""
        from django.utils import timezone
        import random
        import string
        
        year_month = timezone.now().strftime('%Y%m')
        sequential = Order.objects.filter(
            order_number__startswith=f'ORD{year_month}'
        ).count() + 1
        
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"ORD{year_month}{sequential:04d}{random_suffix}"
    
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
    def total_excl_tax(self):
        """Totaal exclusief BTW"""
        return self.subtotal_excl_tax + self.shipping_costs
    
    @property
    def total_incl_tax(self):
        """Totaalprijs inclusief BTW"""
        if self.tax_inclusive:
            return self.subtotal_excl_tax + self.tax_amount + self.shipping_costs
        else:
            total_without_shipping = self.subtotal_excl_tax * (Decimal('1') + (self.tax_rate / Decimal('100')))
            return total_without_shipping + self.shipping_costs
    
    @property
    def amount_paid(self):
        """Totaal betaald bedrag"""
        return self.payments.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
    
    @property
    def amount_due(self):
        """Nog te betalen bedrag"""
        return self.total_incl_tax - self.amount_paid
    
    @property
    def is_paid(self):
        """Is de order volledig betaald?"""
        return self.amount_due <= Decimal('0.00')
    
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
    def days_overdue(self):
        """Dagen achterstallig"""
        from django.utils import timezone
        
        if self.payment_due_date and self.payment_status == PaymentStatus.OVERDUE:
            delta = timezone.now().date() - self.payment_due_date
            return delta.days
        return 0
    
    @property
    def is_overdue(self):
        """Is de betaling achterstallig?"""
        from django.utils import timezone
        
        if self.payment_due_date and self.payment_status != PaymentStatus.PAID:
            return timezone.now().date() > self.payment_due_date
        return False
    
    def confirm(self):
        """Bevestig de order"""
        from django.utils import timezone
        
        if self.status == OrderStatus.DRAFT:
            self.status = OrderStatus.CONFIRMED
            self.confirmed_at = timezone.now()
            self.save()
            
            # TODO: Stuur bevestigingsmail naar klant
            # TODO: Maak factuur aan
            
            return True
        return False
    
    def start_processing(self):
        """Start de verwerking van de order"""
        from django.utils import timezone
        
        if self.status == OrderStatus.CONFIRMED:
            self.status = OrderStatus.PROCESSING
            self.processing_started_at = timezone.now()
            self.save()
            
            # TODO: Update voorraad
            # TODO: Stuur update naar klant
            
            return True
        return False
    
    def mark_as_shipped(self, tracking_number=''):
        """Markeer order als verzonden"""
        from django.utils import timezone
        
        if self.status in [OrderStatus.PROCESSING, OrderStatus.READY_FOR_SHIPMENT]:
            self.status = OrderStatus.SHIPPED
            self.shipped_at = timezone.now()
            if tracking_number:
                self.tracking_number = tracking_number
            self.save()
            
            # TODO: Stuur tracking informatie naar klant
            
            return True
        return False
    
    def mark_as_delivered(self):
        """Markeer order als afgeleverd"""
        from django.utils import timezone
        
        if self.status == OrderStatus.SHIPPED:
            self.status = OrderStatus.DELIVERED
            self.delivered_at = timezone.now()
            self.actual_delivery_date = timezone.now()
            self.save()
            
            # TODO: Stuur leveringsbevestiging naar klant
            # TODO: Vraag review aan
            
            return True
        return False
    
    def cancel(self, reason=''):
        """Annuleer de order"""
        from django.utils import timezone
        
        if self.status not in [OrderStatus.CANCELLED, OrderStatus.COMPLETED, OrderStatus.REFUNDED]:
            self.status = OrderStatus.CANCELLED
            self.cancelled_at = timezone.now()
            if reason:
                self.internal_notes = f"Geannuleerd: {reason}\n{self.internal_notes}"
            self.save()
            
            # TODO: Restock items
            # TODO: Stuur annuleringsmail naar klant
            
            return True
        return False
    
    def complete(self):
        """Markeer order als voltooid"""
        from django.utils import timezone
        
        if self.status == OrderStatus.DELIVERED and self.is_paid:
            self.status = OrderStatus.COMPLETED
            self.completed_at = timezone.now()
            self.save()
            
            # TODO: Archiveer order
            # TODO: Update klantstatistieken
            
            return True
        return False
    
    def create_invoice(self):
        """Creëer een factuur voor deze order"""
        # TODO: Implementeer factuur creatie
        # Dit zou een Invoice object moeten creëren
        pass


class OrderItem(models.Model):
    """
    Items in een order.
    
    TECHNISCHE CONCEPTEN:
    - Line item management
    - Quantity and pricing calculations
    - Stock management integration
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('order')
    )
    
    line_number = models.PositiveIntegerField(
        _('regelnummer'),
        default=1,
        help_text=_('Volgnummer in de order')
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
        related_name='order_items',
        verbose_name=_('product')
    )
    
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
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
        help_text=_('Specifiek BTW percentage voor dit item (laat leeg voor order default)')
    )
    
    # Voorraad tracking
    stock_location = models.CharField(
        _('voorraadlocatie'),
        max_length=100,
        blank=True,
        help_text=_('Locatie in het magazijn')
    )
    
    batch_number = models.CharField(
        _('batchnummer'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Batchnummer (voor traceability)')
    )
    
    serial_number = models.CharField(
        _('serienummer'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Serienummer (voor traceability)')
    )
    
    # Status
    is_delivered = models.BooleanField(
        _('afgeleverd'),
        default=False,
        help_text=_('Is dit item afgeleverd?')
    )
    
    delivered_quantity = models.DecimalField(
        _('afgeleverd aantal'),
        max_digits=10,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_('Aantal eenheden dat is afgeleverd')
    )
    
    delivery_date = models.DateTimeField(
        _('leverdatum item'),
        null=True,
        blank=True,
        help_text=_('Leverdatum voor dit specifieke item')
    )
    
    # Notities
    notes = models.TextField(
        _('notities'),
        blank=True,
        help_text=_('Interne notities over dit item')
    )
    
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
        ordering = ['line_number']
        unique_together = ['order', 'line_number']
    
    def __str__(self):
        return f"{self.order.order_number} - Reg.{self.line_number}: {self.description[:50]}"
    
    @property
    def subtotal_excl_tax(self):
        """Subtotaal voor dit item exclusief BTW"""
        base = self.quantity * self.unit_price
        discount = base * (self.discount_percentage / Decimal('100'))
        return base - discount
    
    @property
    def tax_amount(self):
        """BTW bedrag voor dit item"""
        tax_rate = self.tax_rate if self.tax_rate is not None else self.order.tax_rate
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
    
    @property
    def remaining_quantity(self):
        """Nog af te leveren hoeveelheid"""
        return self.quantity - self.delivered_quantity
    
    @property
    def is_fully_delivered(self):
        """Is dit item volledig afgeleverd?"""
        return self.delivered_quantity >= self.quantity
    
    def mark_as_delivered(self, quantity=None):
        """Markeer (deel van) dit item als afgeleverd"""
        from django.utils import timezone
        
        if quantity is None:
            quantity = self.quantity - self.delivered_quantity
        
        if quantity <= 0:
            return False
        
        # Update afgeleverd aantal
        self.delivered_quantity += quantity
        if self.delivered_quantity >= self.quantity:
            self.is_delivered = True
        
        # Zet leverdatum als nog niet gezet
        if not self.delivery_date:
            self.delivery_date = timezone.now()
        
        self.save()
        
        # Update product stock als dit een product is
        if self.product and self.item_type == 'product':
            # TODO: Update voorraad
            pass
        
        return True
    
    def get_effective_tax_rate(self):
        """Effectief BTW percentage voor dit item"""
        return self.tax_rate if self.tax_rate is not None else self.order.tax_rate


class Payment(models.Model):
    """
    Betalingen voor orders.
    
    TECHNISCHE CONCEPTEN:
    - Multi-payment support
    - Payment gateway integration
    - Transaction tracking
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('order')
    )
    
    payment_number = models.CharField(
        _('betalingnummer'),
        max_length=50,
        unique=True,
        editable=False,
        help_text=_('Uniek betalingnummer')
    )
    
    amount = models.DecimalField(
        _('bedrag'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text=_('Betaald bedrag')
    )
    
    currency = models.CharField(
        _('valuta'),
        max_length=3,
        default='EUR',
        help_text=_('Valuta van de betaling')
    )
    
    payment_method = models.CharField(
        _('betaalmethode'),
        max_length=50,
        choices=[
            ('bank_transfer', _('Bankoverschrijving')),
            ('credit_card', _('Creditcard')),
            ('debit_card', _('Debitcard')),
            ('paypal', _('PayPal')),
            ('ideal', _('iDEAL')),
            ('cash', _('Contant')),
            ('other', _('Overig')),
        ],
        help_text=_('Gebruikte betaalmethode')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=[
            ('pending', _('In afwachting')),
            ('processing', _('In verwerking')),
            ('completed', _('Voltooid')),
            ('failed', _('Mislukt')),
            ('refunded', _('Terugbetaald')),
            ('cancelled', _('Geannuleerd')),
        ],
        default='pending'
    )
    
    transaction_id = models.CharField(
        _('transactie ID'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Transactie ID van de betalingsprovider')
    )
    
    payment_date = models.DateTimeField(
        _('betaaldatum'),
        help_text=_('Datum/tijd van de betaling')
    )
    
    received_date = models.DateTimeField(
        _('ontvangstdatum'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer betaling ontvangen is')
    )
    
    payer_name = models.CharField(
        _('betalersnaam'),
        max_length=200,
        blank=True,
        help_text=_('Naam van de betaler')
    )
    
    payer_email = models.EmailField(
        _('betalers e-mail'),
        max_length=254,
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        _('notities'),
        blank=True,
        help_text=_('Notities over deze betaling')
    )
    
    receipt = models.FileField(
        _('bon'),
        upload_to='payment_receipts/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text=_('Scan of foto van de betalingsbewijs')
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
        verbose_name = _('betaling')
        verbose_name_plural = _('betalingen')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_number']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.payment_number} - €{self.amount} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """Auto-genereren van betalingnummer"""
        if not self.payment_number:
            from django.utils import timezone
            import random
            import string
            
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.payment_number = f"PAY{date_str}{random_str}"
        
        # Update order payment status als betaling voltooid is
        if self.status == 'completed' and not self.received_date:
            from django.utils import timezone
            self.received_date = timezone.now()
            
            # Update order payment status
            order = self.order
            total_paid = order.payments.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            if total_paid >= order.total_incl_tax:
                order.payment_status = PaymentStatus.PAID
            elif total_paid > 0:
                order.payment_status = PaymentStatus.PARTIALLY_PAID
            elif order.payment_due_date and timezone.now().date() > order.payment_due_date:
                order.payment_status = PaymentStatus.OVERDUE
            
            order.save()
        
        super().save(*args, **kwargs)


class OrderTag(models.Model):
    """
    Tags voor categorisatie van orders.
    
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
        verbose_name = _('order tag')
        verbose_name_plural = _('order tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-genereren van slug"""
        from django.utils.text import slugify
        
        if not self.slug:
            self.slug = slugify(self.name)
        
        super().save(*args, **kwargs)


class OrderAttachment(models.Model):
    """
    Bijlagen bij orders.
    
    TECHNISCHE CONCEPTEN:
    - File upload management
    - Document versioning
    - Access control
    """
    
    name = models.CharField(
        _('naam'),
        max_length=200,
        help_text=_('Beschrijvende naam van de bijlage')
    )
    
    file = models.FileField(
        _('bestand'),
        upload_to='order_attachments/%Y/%m/%d/',
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
    
    attachment_type = models.CharField(
        _('bijlage type'),
        max_length=50,
        choices=[
            ('invoice', _('Factuur')),
            ('delivery_note', _('Leveringsbon')),
            ('packing_list', _('Pakbon')),
            ('certificate', _('Certificaat')),
            ('warranty', _('Garantiebewijs')),
            ('photo', _('Foto')),
            ('other', _('Overig')),
        ],
        default='other'
    )
    
    uploaded_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_attachments',
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
        verbose_name = _('order bijlage')
        verbose_name_plural = _('order bijlagen')
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


class OrderHistory(models.Model):
    """
    Audit trail voor order wijzigingen.
    
    TECHNISCHE CONCEPTEN:
    - Change tracking
    - Version history
    - User action logging
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('order')
    )
    
    action = models.CharField(
        _('actie'),
        max_length=50,
        choices=[
            ('created', _('Aangemaakt')),
            ('updated', _('Bijgewerkt')),
            ('status_changed', _('Status gewijzigd')),
            ('confirmed', _('Bevestigd')),
            ('processing_started', _('Verwerking gestart')),
            ('shipped', _('Verzonden')),
            ('delivered', _('Afgeleverd')),
            ('cancelled', _('Geannuleerd')),
            ('completed', _('Voltooid')),
            ('payment_received', _('Betaling ontvangen')),
            ('note_added', _('Notitie toegevoegd')),
            ('attachment_added', _('Bijlage toegevoegd')),
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
        related_name='order_changes',
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
        verbose_name = _('order geschiedenis')
        verbose_name_plural = _('order geschiedenis')
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.action} op {self.changed_at}"