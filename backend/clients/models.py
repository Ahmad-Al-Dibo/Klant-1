import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator, URLValidator
from django.core.exceptions import ValidationError
from core.models import TimeStampedModelWithSoftDelete


class ClientType(models.TextChoices):
    """
    Type klanten.
    """
    INDIVIDUAL = 'individual', _('Particulier')
    BUSINESS = 'business', _('Bedrijf')
    GOVERNMENT = 'government', _('Overheid')
    NON_PROFIT = 'non_profit', _('Non-profit')
    PARTNER = 'partner', _('Partner')


class ClientStatus(models.TextChoices):
    """
    Status van klanten.
    """
    PROSPECT = 'prospect', _('Prospect')
    ACTIVE = 'active', _('Actief')
    INACTIVE = 'inactive', _('Inactief')
    SUSPENDED = 'suspended', _('Geschorst')
    FORMER = 'former', _('Voormalig')


class Client(TimeStampedModelWithSoftDelete):
    """
    Hoofdmodel voor klanten.
    
    TECHNISCHE CONCEPTEN:
    - Klant type management (particulier, bedrijf, etc.)
    - Status workflow
    - Contact en adres informatie
    - Financial information
    """
    
    # Identificatie
    client_number = models.CharField(
        _('klantnummer'),
        max_length=50,
        unique=True,
        editable=False,
        help_text=_('Uniek klantnummer gegenereerd door het systeem')
    )
    
    company_name = models.CharField(
        _('bedrijfsnaam'),
        max_length=200,
        blank=True,
        help_text=_('Officiële bedrijfsnaam (voor bedrijven)')
    )
    
    legal_name = models.CharField(
        _('juridische naam'),
        max_length=200,
        blank=True,
        help_text=_('Juridische naam (kan afwijken van bedrijfsnaam)')
    )
    
    # Type en status
    client_type = models.CharField(
        _('klanttype'),
        max_length=20,
        choices=ClientType.choices,
        default=ClientType.BUSINESS,
        help_text=_('Type klant')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=ClientStatus.choices,
        default=ClientStatus.PROSPECT,
        help_text=_('Huidige status van de klant')
    )
    
    # Contact informatie
    email = models.EmailField(
        _('e-mailadres'),
        max_length=254,
        validators=[EmailValidator()],
        help_text=_('Primair e-mailadres')
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Telefoonnummer moet in het formaat: '+31612345678'. Maximaal 15 cijfers.")
    )
    
    phone = models.CharField(
        _('telefoonnummer'),
        validators=[phone_regex],
        max_length=17,
        help_text=_('Primair telefoonnummer')
    )
    
    website = models.URLField(
        _('website'),
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text=_('Website URL')
    )
    
    # Adres informatie (hoofdkantoor)
    street = models.CharField(
        _('straat'),
        max_length=200,
        blank=True,
        help_text=_('Straatnaam en huisnummer')
    )
    
    postal_code = models.CharField(
        _('postcode'),
        max_length=10,
        blank=True,
        help_text=_('Postcode')
    )
    
    city = models.CharField(
        _('stad'),
        max_length=100,
        blank=True,
        help_text=_('Stad')
    )
    
    country = models.CharField(
        _('land'),
        max_length=100,
        default='Nederland',
        help_text=_('Land')
    )
    
    # Zakelijke informatie
    tax_number = models.CharField(
        _('btw-nummer'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('BTW-nummer')
    )
    
    chamber_of_commerce = models.CharField(
        _('kvk-nummer'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Kamer van Koophandel nummer')
    )
    
    industry = models.CharField(
        _('branche'),
        max_length=100,
        blank=True,
        help_text=_('Industrie of branche')
    )
    
    # Financiële informatie
    credit_limit = models.DecimalField(
        _('kredietlimiet'),
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_('Maximaal kredietbedrag')
    )
    
    payment_terms = models.CharField(
        _('betalingsvoorwaarden'),
        max_length=50,
        default='30 dagen',
        help_text=_('Standaard betalingsvoorwaarden')
    )
    
    currency = models.CharField(
        _('valuta'),
        max_length=3,
        default='EUR',
        help_text=_('Voorkeursvaluta')
    )
    
    # Metadata
    source = models.CharField(
        _('bron'),
        max_length=100,
        blank=True,
        help_text=_('Hoe is de klant bij ons terechtgekomen?')
    )
    
    tags = models.ManyToManyField(
        'ClientTag',
        blank=True,
        related_name='clients',
        verbose_name=_('tags'),
        help_text=_('Tags voor categorisatie')
    )
    
    assigned_to = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_clients',
        verbose_name=_('toegewezen aan'),
        help_text=_('Accountmanager of verkoper')
    )
    
    # Notities
    internal_notes = models.TextField(
        _('interne notities'),
        blank=True,
        help_text=_('Interne notities over deze klant')
    )
    
    class Meta:
        verbose_name = _('klant')
        verbose_name_plural = _('klanten')
        ordering = ['company_name', 'client_number']
        indexes = [
            models.Index(fields=['client_number']),
            models.Index(fields=['company_name']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['client_type', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        if self.company_name:
            return f"{self.company_name} ({self.client_number})"
        return f"Klant {self.client_number}"
    
    def save(self, *args, **kwargs):
        """Auto-genereren van klantnummer bij aanmaak"""
        if not self.client_number:
            self.client_number = self.generate_client_number()
        
        # Voor particulieren: gebruik e-mail als bedrijfsnaam indien leeg
        if self.client_type == ClientType.INDIVIDUAL and not self.company_name:
            self.company_name = self.email
        
        super().save(*args, **kwargs)
    
    def generate_client_number(self):
        """Genereer uniek klantnummer"""
        from django.utils import timezone
        import random
        import string
        
        prefix = 'CUST'
        year_month = timezone.now().strftime('%y%m')
        sequential = Client.objects.filter(
            client_number__startswith=f'{prefix}{year_month}'
        ).count() + 1
        
        random_suffix = ''.join(random.choices(string.ascii_uppercase, k=2))
        
        return f"{prefix}{year_month}{sequential:04d}{random_suffix}"
    
    def clean(self):
        """Valideer klantgegevens"""
        # Bedrijven moeten een bedrijfsnaam hebben
        if self.client_type != ClientType.INDIVIDUAL and not self.company_name:
            raise ValidationError({
                'company_name': _('Bedrijfsnaam is verplicht voor bedrijven')
            })
    
    @property
    def full_address(self):
        """Volledig geformatteerd adres"""
        parts = []
        if self.street:
            parts.append(self.street)
        if self.postal_code or self.city:
            parts.append(f"{self.postal_code} {self.city}".strip())
        if self.country and self.country != 'Nederland':
            parts.append(self.country)
        
        return ', '.join(parts) if parts else _('Geen adres opgegeven')
    
    @property
    def is_active_client(self):
        """Is dit een actieve klant?"""
        return self.status == ClientStatus.ACTIVE
    
    @property
    def display_name(self):
        """Display naam voor UI"""
        if self.company_name:
            return self.company_name
        return self.email
    
    def activate(self):
        """Activeer de klant"""
        self.status = ClientStatus.ACTIVE
        self.save()
    
    def deactivate(self):
        """Deactiveer de klant"""
        self.status = ClientStatus.INACTIVE
        self.save()


class ClientContact(models.Model):
    """
    Contactpersonen bij klanten.
    
    TECHNISCHE CONCEPTEN:
    - Multiple contacts per client
    - Role-based contact information
    - Primary contact designation
    """
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name=_('klant')
    )
    
    # Persoonlijke informatie
    first_name = models.CharField(
        _('voornaam'),
        max_length=100,
        help_text=_('Voornaam')
    )
    
    last_name = models.CharField(
        _('achternaam'),
        max_length=100,
        help_text=_('Achternaam')
    )
    
    email = models.EmailField(
        _('e-mailadres'),
        max_length=254,
        validators=[EmailValidator()],
        help_text=_('E-mailadres van de contactpersoon')
    )
    
    phone = models.CharField(
        _('telefoonnummer'),
        validators=[Client.phone_regex],
        max_length=17,
        help_text=_('Telefoonnummer van de contactpersoon')
    )
    
    mobile = models.CharField(
        _('mobiel nummer'),
        validators=[Client.phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text=_('Mobiel telefoonnummer')
    )
    
    # Rol en functie
    job_title = models.CharField(
        _('functietitel'),
        max_length=100,
        blank=True,
        help_text=_('Functietitel')
    )
    
    department = models.CharField(
        _('afdeling'),
        max_length=100,
        blank=True,
        help_text=_('Afdeling')
    )
    
    role = models.CharField(
        _('rol'),
        max_length=50,
        choices=[
            ('decision_maker', _('Beslisser')),
            ('influencer', _('Beïnvloeder')),
            ('user', _('Gebruiker')),
            ('technical', _('Technisch contact')),
            ('financial', _('Financieel contact')),
            ('general', _('Algemeen contact')),
        ],
        default='general',
        help_text=_('Rol binnen het bedrijf')
    )
    
    # Status
    is_primary = models.BooleanField(
        _('primaire contactpersoon'),
        default=False,
        help_text=_('Is dit de primaire contactpersoon?')
    )
    
    is_active = models.BooleanField(
        _('actief'),
        default=True,
        help_text=_('Is deze contactpersoon actief?')
    )
    
    # Voorkeuren
    preferred_contact_method = models.CharField(
        _('voorkeur communicatiemethode'),
        max_length=20,
        choices=[
            ('email', _('E-mail')),
            ('phone', _('Telefoon')),
            ('sms', _('SMS')),
            ('whatsapp', _('WhatsApp')),
        ],
        default='email'
    )
    
    language = models.CharField(
        _('taalvoorkeur'),
        max_length=10,
        default='nl',
        choices=[
            ('nl', _('Nederlands')),
            ('en', _('Engels')),
            ('de', _('Duits')),
            ('ar', _('Arabisch')),
        ]
    )
    
    # Notities
    notes = models.TextField(
        _('notities'),
        blank=True,
        help_text=_('Notities over deze contactpersoon')
    )
    
    # Metadata
    created_at = models.DateTimeField(
        _('aangemaakt op'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('bijgewerkt op'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('klantcontact')
        verbose_name_plural = _('klantcontacten')
        ordering = ['client', '-is_primary', 'last_name', 'first_name']
        unique_together = ['client', 'email']
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.client}"
    
    def get_full_name(self):
        """Volledige naam"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        """Zorg dat er maar één primaire contactpersoon is per klant"""
        if self.is_primary:
            # Zet alle andere contacten van deze klant op niet-primair
            ClientContact.objects.filter(
                client=self.client,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """Property voor volledige naam"""
        return self.get_full_name()


class Address(models.Model):
    """
    Adressen voor klanten (meerdere adressen per klant mogelijk).
    
    TECHNISCHE CONCEPTEN:
    - Multiple addresses per client
    - Address type classification
    - Geographic information
    """
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('klant')
    )
    
    # Adres informatie
    address_type = models.CharField(
        _('adrestype'),
        max_length=20,
        choices=[
            ('billing', _('Factuuradres')),
            ('shipping', _('Afleveradres')),
            ('office', _('Kantoor')),
            ('warehouse', _('Magazijn')),
            ('home', _('Thuisadres')),
            ('other', _('Overig')),
        ],
        default='billing',
        help_text=_('Type adres')
    )
    
    street = models.CharField(
        _('straat'),
        max_length=200,
        help_text=_('Straatnaam en huisnummer')
    )
    
    postal_code = models.CharField(
        _('postcode'),
        max_length=10,
        help_text=_('Postcode')
    )
    
    city = models.CharField(
        _('stad'),
        max_length=100,
        help_text=_('Stad')
    )
    
    state = models.CharField(
        _('provincie/staat'),
        max_length=100,
        blank=True,
        help_text=_('Provincie of staat')
    )
    
    country = models.CharField(
        _('land'),
        max_length=100,
        default='Nederland',
        help_text=_('Land')
    )
    
    # Geografische informatie
    latitude = models.DecimalField(
        _('breedtegraad'),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_('Geografische breedtegraad')
    )
    
    longitude = models.DecimalField(
        _('lengtegraad'),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_('Geografische lengtegraad')
    )
    
    # Status
    is_primary = models.BooleanField(
        _('primair adres'),
        default=False,
        help_text=_('Is dit het primaire adres van dit type?')
    )
    
    is_active = models.BooleanField(
        _('actief'),
        default=True,
        help_text=_('Is dit adres actief in gebruik?')
    )
    
    # Contact informatie
    contact_person = models.ForeignKey(
        ClientContact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='addresses',
        verbose_name=_('contactpersoon'),
        help_text=_('Contactpersoon op dit adres')
    )
    
    phone = models.CharField(
        _('telefoonnummer'),
        validators=[Client.phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text=_('Telefoonnummer voor dit adres')
    )
    
    # Notities
    instructions = models.TextField(
        _('instructies'),
        blank=True,
        help_text=_('Speciale instructies voor dit adres')
    )
    
    notes = models.TextField(
        _('notities'),
        blank=True,
        help_text=_('Interne notities over dit adres')
    )
    
    # Metadata
    created_at = models.DateTimeField(
        _('aangemaakt op'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('bijgewerkt op'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('adres')
        verbose_name_plural = _('adressen')
        ordering = ['client', 'address_type', '-is_primary']
    
    def __str__(self):
        return f"{self.get_full_address()} ({self.get_address_type_display()})"
    
    def get_full_address(self):
        """Volledig geformatteerd adres"""
        parts = [self.street]
        
        city_line = f"{self.postal_code} {self.city}".strip()
        if city_line:
            parts.append(city_line)
        
        if self.state:
            parts.append(self.state)
        
        if self.country and self.country != 'Nederland':
            parts.append(self.country)
        
        return ', '.join(parts)
    
    @property
    def full_address(self):
        """Property voor volledig adres"""
        return self.get_full_address()
    
    def save(self, *args, **kwargs):
        """Zorg dat er maar één primair adres is per type per klant"""
        if self.is_primary:
            # Zet alle andere adressen van dit type voor deze klant op niet-primair
            Address.objects.filter(
                client=self.client,
                address_type=self.address_type,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)


class ClientTag(models.Model):
    """
    Tags voor klant categorisatie.
    
    TECHNISCHE CONCEPTEN:
    - Flexible categorization
    - Color coding
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
        verbose_name = _('klant tag')
        verbose_name_plural = _('klant tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-genereren van slug"""
        from django.utils.text import slugify
        
        if not self.slug:
            self.slug = slugify(self.name)
        
        super().save(*args, **kwargs)


class ClientNote(TimeStampedModelWithSoftDelete):
    """
    Notities voor klanten.
    
    TECHNISCHE CONCEPTEN:
    - Rich text notes
    - Categorization
    - Privacy levels
    """
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('klant')
    )
    
    title = models.CharField(
        _('titel'),
        max_length=200,
        help_text=_('Titel van de notitie')
    )
    
    content = models.TextField(
        _('inhoud'),
        help_text=_('Inhoud van de notitie')
    )
    
    note_type = models.CharField(
        _('notitie type'),
        max_length=50,
        choices=[
            ('general', _('Algemeen')),
            ('meeting', _('Vergadering')),
            ('call', _('Telefoongesprek')),
            ('email', _('E-mail')),
            ('task', _('Taak')),
            ('issue', _('Probleem')),
            ('opportunity', _('Kans')),
            ('other', _('Overig')),
        ],
        default='general'
    )
    
    privacy_level = models.CharField(
        _('privacy niveau'),
        max_length=20,
        choices=[
            ('public', _('Publiek (alle medewerkers)')),
            ('team', _('Team (alleen toegewezen team)')),
            ('private', _('Privé (alleen auteur)')),
            ('confidential', _('Vertrouwelijk (management)')),
        ],
        default='team'
    )
    
    is_pinned = models.BooleanField(
        _('vastgezet'),
        default=False,
        help_text=_('Is deze notitie vastgezet bovenaan?')
    )
    
    due_date = models.DateTimeField(
        _('vervaldatum'),
        blank=True,
        null=True,
        help_text=_('Vervaldatum voor actie-items')
    )
    
    class Meta:
        verbose_name = _('klantnotitie')
        verbose_name_plural = _('klantnotities')
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.client}"