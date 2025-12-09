import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel

class ContactCategory(models.Model):
    """
    Categorieën voor contactverzoeken voor betere organisatie.
    
    TECHNISCHE CONCEPTEN:
    - Slug field voor URL identificatie
    - Hierarchische structuur mogelijk (parent-child)
    - Prioriteit voor routing naar verschillende afdelingen
    """
    
    CATEGORY_TYPES = [
        ('general', _('Algemeen')),
        ('sales', _('Verkoop')),
        ('support', _('Ondersteuning')),
        ('technical', _('Technisch')),
        ('complaint', _('Klacht')),
        ('quote_request', _('Offerte aanvraag')),
        ('service_request', _('Dienst aanvraag')),
        ('feedback', _('Feedback')),
        ('other', _('Overig')),
    ]
    
    name = models.CharField(
        _('naam'),
        max_length=100,
        unique=True,
        help_text=_('Naam van de categorie')
    )
    
    slug = models.SlugField(
        _('slug'),
        max_length=120,
        unique=True,
        help_text=_('URL-vriendelijke naam')
    )
    
    category_type = models.CharField(
        _('categorie type'),
        max_length=20,
        choices=CATEGORY_TYPES,
        default='general',
        help_text=_('Type categorie voor interne routing')
    )
    
    description = models.TextField(
        _('beschrijving'),
        blank=True,
        help_text=_('Beschrijving van wanneer deze categorie gebruikt moet worden')
    )
    
    email_recipient = models.EmailField(
        _('e-mail ontvanger'),
        blank=True,
        null=True,
        help_text=_('Specifieke e-mail voor deze categorie (laat leeg voor default)')
    )
    
    is_active = models.BooleanField(
        _('actief'),
        default=True,
        help_text=_('Of deze categorie beschikbaar is voor gebruik')
    )\
    
    priority = models.PositiveIntegerField(
        _('prioriteit'),
        default=5,
        help_text=_('Prioriteit (1=hoogste, 10=laagste) voor response tijd')
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_('hoofdcategorie')
    )
    
    class Meta:
        verbose_name = _('contactcategorie')
        verbose_name_plural = _('contactcategorieën')
        ordering = ['priority', 'name']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['category_type', 'is_active']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f"/api/v1/contact/categories/{self.slug}/"
    
    def clean(self):
        """Validatie om circulaire referenties te voorkomen"""
        if self.parent and self.parent == self:
            raise ValidationError(_('Een categorie kan niet zijn eigen ouder zijn'))
        
        if self.parent and self.parent.parent and self.parent.parent == self:
            raise ValidationError(_('Circulaire referentie gedetecteerd'))

    def save(self, *args, **kwargs):
        """Auto-genereren van slug indien niet opgegeven"""
        from django.utils.text import slugify
        
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Zorg voor unieke slug
        original_slug = self.slug
        counter = 1
        while ContactCategory.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save(*args, **kwargs)


class ContactMessage(TimeStampedModel):
    """
    Hoofdmodel voor contactberichten van gebruikers.
    
    TECHNISCHE CONCEPTEN:
    - UUID voor veilige referentie
    - Status tracking voor workflow
    - Auto-assignment van categorieën
    - Audit trail met TimeStampedModel
    """
    
    STATUS_CHOICES = [
        ('new', _('Nieuw')),
        ('read', _('Gelezen')),
        ('in_progress', _('In behandeling')),
        ('awaiting_reply', _('Wacht op antwoord')),
        ('resolved', _('Afgehandeld')),
        ('closed', _('Gesloten')),
        ('spam', _('Spam')),
    ]
    
    # Unieke identificatie
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_('UUID')
    )
    
    # Referentie nummer voor klant
    reference_number = models.CharField(
        _('referentie nummer'),
        max_length=50,
        unique=True,
        editable=False,
        help_text=_('Uniek referentienummer voor dit bericht')
    )
    
    # Verzender informatie
    full_name = models.CharField(
        _('volledige naam'),
        max_length=200,
        help_text=_('Voor- en achternaam van de verzender')
    )
    
    email = models.EmailField(
        _('e-mailadres'),
        max_length=254,
        validators=[EmailValidator()],
        help_text=_('E-mailadres voor antwoord')
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Telefoonnummer moet in het formaat: '+31612345678'. Maximaal 15 cijfers.")
    )
    
    phone_number = models.CharField(
        _('telefoonnummer'),
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text=_('Optioneel telefoonnummer')
    )
    
    company_name = models.CharField(
        _('bedrijfsnaam'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Optionele bedrijfsnaam')
    )
    
    # Bericht inhoud
    category = models.ForeignKey(
        ContactCategory,
        on_delete=models.PROTECT,
        related_name='messages',
        verbose_name=_('categorie'),
        help_text=_('Categorie van het bericht')
    )
    
    subject = models.CharField(
        _('onderwerp'),
        max_length=200,
        help_text=_('Onderwerp van het bericht')
    )
    
    message = models.TextField(
        _('bericht'),
        help_text=_('Inhoud van het bericht')
    )
    
    # Status en workflow
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        help_text=_('Huidige status van het bericht')
    )
    
    priority = models.PositiveIntegerField(
        _('prioriteit'),
        default=5,
        help_text=_('Prioriteit van het bericht (1=hoogste, 10=laagste)')
    )
    
    # Tracking en analytics
    ip_address = models.GenericIPAddressField(
        _('IP adres'),
        blank=True,
        null=True,
        help_text=_('IP adres van de verzender')
    )
    
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        null=True,
        help_text=_('Browser/device informatie')
    )
    
    page_url = models.URLField(
        _('pagina URL'),
        blank=True,
        null=True,
        max_length=500,
        help_text=_('URL waar het formulier is ingediend')
    )
    
    # Response tracking
    assigned_to = models.ForeignKey(
        'authentication.CustomUser',  # String referentie
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='assigned_contact_messages',
        verbose_name=_('toegewezen aan'),
        help_text=_('Medewerker die dit bericht behandelt')
    )
    
    related_quote = models.ForeignKey(
        'quotes.Quote',  # String referentie
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='contact_messages',
        verbose_name=_('gerelateerde offerte')
    )
    
    response_notes = models.TextField(
        _('antwoord notities'),
        blank=True,
        null=True,
        help_text=_('Interne notities over de afhandeling')
    )
    
    responded_at = models.DateTimeField(
        _('beantwoord op'),
        blank=True,
        null=True,
        help_text=_('Datum/tijd van laatste antwoord')
    )
    
    # Optionele relaties
    related_product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='contact_messages',
        verbose_name=_('gerelateerd product')
    )
    
    related_service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='contact_messages',
        verbose_name=_('gerelateerde dienst')
    )
    
    class Meta:
        verbose_name = _('contactbericht')
        verbose_name_plural = _('contactberichten')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['priority', 'created_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.reference_number} - {self.subject}"
    
    def get_absolute_url(self):
        return f"/api/v1/contact/messages/{self.uuid}/"
    
    def clean(self):
        """Validatie van business regels"""
        # Prioriteit moet tussen 1 en 10 zijn
        if not 1 <= self.priority <= 10:
            raise ValidationError(_('Prioriteit moet tussen 1 en 10 liggen'))
        
        # Bericht moet een minimale lengte hebben
        if len(self.message.strip()) < 10:
            raise ValidationError(_('Bericht moet minimaal 10 karakters bevatten'))
    
    def save(self, *args, **kwargs):
        """Auto-genereren van referentienummer bij aanmaak"""
        if not self.reference_number:
            from django.utils import timezone
            import random
            import string
            
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.reference_number = f"CONTACT-{date_str}-{random_str}"
            
            # Zorg dat het uniek is
            while ContactMessage.objects.filter(reference_number=self.reference_number).exists():
                random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                self.reference_number = f"CONTACT-{date_str}-{random_str}"
        
        # Auto-set priority van category als niet expliciet opgegeven
        if self.pk is None and not self.priority:  # Only on create
            self.priority = self.category.priority if self.category else 5
        
        super().save(*args, **kwargs)
    
    def mark_as_read(self, user=None):
        """Markeer bericht als gelezen"""
        if self.status == 'new':
            self.status = 'read'
            if user:
                self.response_notes = f"Gelezen door {user.email} op {timezone.now().strftime('%Y-%m-%d %H:%M')}\n{self.response_notes or ''}"
            self.save(update_fields=['status', 'response_notes'])
    
    def assign_to(self, user):
        """Wijs bericht toe aan een gebruiker"""
        self.assigned_to = user
        self.status = 'in_progress'
        self.response_notes = f"Toegewezen aan {user.email} op {timezone.now().strftime('%Y-%m-%d %H:%M')}\n{self.response_notes or ''}"
        self.save(update_fields=['assigned_to', 'status', 'response_notes'])
    
    def add_response_note(self, note, user=None):
        """Voeg een antwoord notitie toe"""
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
        user_info = f" door {user.email}" if user else ""
        
        self.response_notes = f"[{timestamp}{user_info}]: {note}\n{self.response_notes or ''}"
        self.save(update_fields=['response_notes'])
    
    @property
    def response_time(self):
        """Bereken response tijd"""
        if self.responded_at and self.created_at:
            return self.responded_at - self.created_at
        return None
    
    @property
    def is_high_priority(self):
        """Is dit een hoge prioriteit bericht?"""
        return self.priority <= 3
    
    @property
    def is_urgent(self):
        """Is dit een urgente prioriteit bericht?"""
        return self.priority == 1


class ContactAttachment(models.Model):
    """
    Bijlagen voor contactberichten.
    
    TECHNISCHE CONCEPTEN:
    - File upload met validatie
    - Virus scanning mogelijkheid
    - File type restricties
    """
    
    ALLOWED_FILE_TYPES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ]
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    message = models.ForeignKey(
        ContactMessage,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('bericht')
    )
    
    file = models.FileField(
        _('bestand'),
        upload_to='contact_attachments/%Y/%m/%d/',
        help_text=_('Bijlage bij het bericht')
    )
    
    file_name = models.CharField(
        _('bestandsnaam'),
        max_length=255,
        blank=True,
        help_text=_('Originele bestandsnaam')
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
    
    uploaded_at = models.DateTimeField(
        _('geüpload op'),
        auto_now_add=True
    )
    
    is_safe = models.BooleanField(
        _('veilig gescand'),
        default=True,
        help_text=_('Indicatie of het bestand veilig is gescand')
    )
    
    class Meta:
        verbose_name = _('contactbijlage')
        verbose_name_plural = _('contactbijlagen')
        ordering = ['uploaded_at']
        indexes = [
            models.Index(fields=['message', 'uploaded_at']),
        ]
    
    def __str__(self):
        return self.file_name or self.file.name
    
    def clean(self):
        """Validatie van bestand"""
        from django.core.exceptions import ValidationError
        
        if self.file:
            # Controleer bestandsgrootte
            if self.file.size > self.MAX_FILE_SIZE:
                raise ValidationError(
                    _('Bestand mag niet groter zijn dan 10MB')
                )
            
            # Controleer bestandstype
            import magic
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(self.file.read(1024))
            
            if file_type not in self.ALLOWED_FILE_TYPES:
                raise ValidationError(
                    _('Bestandstype niet toegestaan. Toegestane types: {}'.format(
                        ', '.join([t.split('/')[-1] for t in self.ALLOWED_FILE_TYPES])
                    ))
                )
            
            self.file_type = file_type
            self.file_size = self.file.size
    
    def save(self, *args, **kwargs):
        """Opslaan met automatische file_name extractie"""
        if self.file and not self.file_name:
            self.file_name = self.file.name
        
        super().save(*args, **kwargs)
    
    @property
    def file_extension(self):
        """Haal bestandsextensie op"""
        if self.file_name:
            return self.file_name.split('.')[-1].lower()
        return ''
    
    @property
    def is_image(self):
        """Is dit een afbeelding?"""
        return self.file_type and self.file_type.startswith('image/')


class NewsletterSubscriber(models.Model):
    """
    Nieuwsbrief inschrijvingen.
    
    TECHNISCHE CONCEPTEN:
    - Double opt-in flow
    - GDPR compliance
    - Subscription preferences
    """
    
    email = models.EmailField(
        _('e-mailadres'),
        unique=True,
        max_length=254,
        validators=[EmailValidator()],
        help_text=_('E-mailadres voor nieuwsbrief')
    )
    
    full_name = models.CharField(
        _('volledige naam'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Optionele volledige naam')
    )
    
    subscription_token = models.UUIDField(
        _('inschrijvingstoken'),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    
    is_confirmed = models.BooleanField(
        _('bevestigd'),
        default=False,
        help_text=_('Heeft de gebruiker de inschrijving bevestigd?')
    )
    
    confirmed_at = models.DateTimeField(
        _('bevestigd op'),
        blank=True,
        null=True
    )
    
    subscription_preferences = models.JSONField(
        _('inschrijvingsvoorkeuren'),
        default=dict,
        help_text=_('Voorkeuren voor type updates')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP adres'),
        blank=True,
        null=True,
        help_text=_('IP adres tijdens inschrijving')
    )
    
    is_active = models.BooleanField(
        _('actief'),
        default=True,
        help_text=_('Is de inschrijving actief?')
    )
    
    unsubscribe_token = models.UUIDField(
        _('uitschrijftoken'),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    
    unsubscribed_at = models.DateTimeField(
        _('uitgeschreven op'),
        blank=True,
        null=True
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
        verbose_name = _('nieuwsbriefinschrijving')
        verbose_name_plural = _('nieuwsbriefinschrijvingen')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['is_confirmed', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.email
    
    def confirm_subscription(self):
        """Bevestig de inschrijving"""
        from django.utils import timezone
        
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=['is_confirmed', 'confirmed_at'])
    
    def unsubscribe(self):
        """Schrijf uit van nieuwsbrief"""
        from django.utils import timezone
        
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at'])
    
    def resubscribe(self):
        """Herschrijf in voor nieuwsbrief"""
        self.is_active = True
        self.unsubscribed_at = None
        self.save(update_fields=['is_active', 'unsubscribed_at'])
    
    @property
    def subscription_duration(self):
        """Hoe lang is de gebruiker ingeschreven?"""
        if self.confirmed_at:
            from django.utils import timezone
            return timezone.now() - self.confirmed_at
        return None