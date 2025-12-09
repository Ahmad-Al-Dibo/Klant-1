import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """
    Custom manager voor CustomUser model met email als username.
    
    TECHNISCHE CONCEPTEN:
    - Custom user manager voor email-based authenticatie
    - Methoden voor het aanmaken van users en superusers
    - Validatie van verplichte velden
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Creëer en retourneer een gebruiker met email en wachtwoord.
        """
        if not email:
            raise ValueError(_('Het e-mailadres moet ingevuld worden'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creëer en retourneer een superuser met email en wachtwoord.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser moet is_staff=True hebben'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser moet is_superuser=True hebben'))
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Aangepast User model met email als primary identifier.
    
    TECHNISCHE CONCEPTEN:
    - AbstractBaseUser voor basis authenticatie functionaliteit
    - PermissionsMixin voor permissie systeem
    - Email als username field (geen username veld)
    - Uitgebreide gebruikersprofiel informatie
    """
    
    # Identificatie
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('UUID')
    )
    
    email = models.EmailField(
        _('e-mailadres'),
        unique=True,
        max_length=254,
        validators=[EmailValidator()],
        help_text=_('Primair e-mailadres voor inloggen en communicatie')
    )
    
    # Persoonlijke informatie
    first_name = models.CharField(
        _('voornaam'),
        max_length=150,
        blank=True,
        help_text=_('Voornaam van de gebruiker')
    )
    
    last_name = models.CharField(
        _('achternaam'),
        max_length=150,
        blank=True,
        help_text=_('Achternaam van de gebruiker')
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
        help_text=_('Primair telefoonnummer')
    )
    
    # Status vlaggen
    is_active = models.BooleanField(
        _('actief'),
        default=True,
        help_text=_('Geeft aan of de gebruiker actief is. '
                   'In plaats van accounts te verwijderen, zet deze op False.')
    )
    
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Geeft aan of de gebruiker kan inloggen op de admin site.')
    )
    
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_('Geeft aan of de gebruiker alle permissies heeft zonder ze expliciet toe te wijzen.')
    )
    
    # Datums
    date_joined = models.DateTimeField(
        _('aanmelddatum'),
        default=timezone.now,
        help_text=_('Datum wanneer de gebruiker zich registreerde')
    )
    
    last_login = models.DateTimeField(
        _('laatste login'),
        blank=True,
        null=True,
        help_text=_('Datum van de laatste succesvolle login')
    )
    
    # Profiel informatie
    profile_picture = models.ImageField(
        _('profielafbeelding'),
        upload_to='profile_pictures/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text=_('Optionele profielfoto')
    )
    
    job_title = models.CharField(
        _('functietitel'),
        max_length=100,
        blank=True,
        help_text=_('Functietitel binnen het bedrijf')
    )
    
    department = models.CharField(
        _('afdeling'),
        max_length=100,
        blank=True,
        help_text=_('Afdeling waar de gebruiker werkt')
    )
    
    # Voorkeuren
    language = models.CharField(
        _('taalvoorkeur'),
        max_length=10,
        default='nl',
        choices=[
            ('nl', _('Nederlands')),
            ('en', _('Engels')),
            ('de', _('Duits')),
            ('ar', _('Arabisch')),
        ],
        help_text=_('Voorkeurstaal voor de interface')
    )
    
    timezone = models.CharField(
        _('tijdzone'),
        max_length=50,
        default='Europe/Amsterdam',
        help_text=_('Voorkeur tijdzone')
    )
    
    email_notifications = models.BooleanField(
        _('e-mail notificaties'),
        default=True,
        help_text=_('Of de gebruiker e-mail notificaties wil ontvangen')
    )
    
    # Metadata
    notes = models.TextField(
        _('notities'),
        blank=True,
        help_text=_('Interne notities over deze gebruiker')
    )
    
    # Manager
    objects = CustomUserManager()
    
    # Velden voor authenticatie
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('gebruiker')
        verbose_name_plural = _('gebruikers')
        ordering = ['email']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['date_joined']),
            models.Index(fields=['last_login']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """
        Retourneer de volledige naam van de gebruiker.
        """
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def get_short_name(self):
        """
        Retourneer de korte naam van de gebruiker.
        """
        return self.first_name
    
    def clean(self):
        """
        Valideer het gebruikersobject.
        """
        super().clean()
        
        # Valideer e-mail
        self.email = self.__class__.objects.normalize_email(self.email)
        
        # Valideer naam
        if self.first_name and len(self.first_name.strip()) < 1:
            raise ValidationError({'first_name': _('Voornaam is verplicht')})
    
    @property
    def is_employee(self):
        """
        Is deze gebruiker een medewerker?
        """
        return self.is_staff
    
    @property
    def is_admin(self):
        """
        Is deze gebruiker een administrator?
        """
        return self.is_superuser
    
    @property
    def full_name(self):
        """
        Property voor volledige naam.
        """
        return self.get_full_name()
    
    @property
    def initials(self):
        """
        Initialen van de gebruiker.
        """
        initials = ''
        if self.first_name:
            initials += self.first_name[0].upper()
        if self.last_name:
            initials += self.last_name[0].upper()
        return initials or '??'


class UserProfile(models.Model):
    """
    Uitgebreid profiel voor gebruikers.
    
    TECHNISCHE CONCEPTEN:
    - One-to-one relatie met CustomUser
    - Uitgebreide gebruikersinformatie
    - Profiel-specifieke instellingen
    """
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('gebruiker')
    )
    
    # Contact informatie
    secondary_email = models.EmailField(
        _('secundair e-mailadres'),
        blank=True,
        null=True,
        help_text=_('Optioneel secundair e-mailadres')
    )
    
    secondary_phone = models.CharField(
        _('secundair telefoonnummer'),
        validators=[CustomUser.phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text=_('Optioneel secundair telefoonnummer')
    )
    
    # Adres informatie
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
    
    # Persoonlijke informatie
    date_of_birth = models.DateField(
        _('geboortedatum'),
        blank=True,
        null=True,
        help_text=_('Geboortedatum')
    )
    
    gender = models.CharField(
        _('geslacht'),
        max_length=20,
        blank=True,
        choices=[
            ('male', _('Man')),
            ('female', _('Vrouw')),
            ('other', _('Anders')),
            ('prefer_not_to_say', _('Zeg ik liever niet')),
        ],
        help_text=_('Geslacht')
    )
    
    # Social media
    linkedin_url = models.URLField(
        _('LinkedIn URL'),
        blank=True,
        null=True,
        help_text=_('LinkedIn profiel URL')
    )
    
    twitter_handle = models.CharField(
        _('Twitter handle'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Twitter gebruikersnaam')
    )
    
    # Werk informatie
    employee_id = models.CharField(
        _('medewerker ID'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Uniek medewerkersnummer')
    )
    
    hire_date = models.DateField(
        _('in dienst vanaf'),
        blank=True,
        null=True,
        help_text=_('Datum van indiensttreding')
    )
    
    # Voorkeuren en instellingen
    theme = models.CharField(
        _('thema'),
        max_length=20,
        default='light',
        choices=[
            ('light', _('Licht')),
            ('dark', _('Donker')),
            ('auto', _('Automatisch')),
        ],
        help_text=_('Interface thema voorkeur')
    )
    
    notification_preferences = models.JSONField(
        _('notificatie voorkeuren'),
        default=dict,
        help_text=_('Gedetailleerde notificatie voorkeuren')
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
        verbose_name = _('gebruikersprofiel')
        verbose_name_plural = _('gebruikersprofielen')
    
    def __str__(self):
        return f"Profiel van {self.user.email}"
    
    @property
    def full_address(self):
        """
        Volledig geformatteerd adres.
        """
        parts = []
        if self.street:
            parts.append(self.street)
        if self.postal_code or self.city:
            parts.append(f"{self.postal_code} {self.city}".strip())
        if self.country and self.country != 'Nederland':
            parts.append(self.country)
        
        return ', '.join(parts) if parts else _('Geen adres opgegeven')
    
    @property
    def age(self):
        """
        Leeftijd in jaren.
        """
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class UserActivityLog(models.Model):
    """
    Logboek voor gebruikersactiviteiten.
    
    TECHNISCHE CONCEPTEN:
    - Audit logging voor gebruikersacties
    - Security monitoring
    - Compliance logging
    """
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name=_('gebruiker'),
        null=True,
        blank=True
    )
    
    action = models.CharField(
        _('actie'),
        max_length=100,
        help_text=_('Beschrijving van de uitgevoerde actie')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP adres'),
        blank=True,
        null=True,
        help_text=_('IP adres van waar de actie werd uitgevoerd')
    )
    
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        null=True,
        help_text=_('Browser/device informatie')
    )
    
    details = models.JSONField(
        _('details'),
        default=dict,
        help_text=_('Gedetailleerde informatie over de actie')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=[
            ('success', _('Succes')),
            ('failed', _('Mislukt')),
            ('warning', _('Waarschuwing')),
        ],
        default='success'
    )
    
    timestamp = models.DateTimeField(
        _('tijdstip'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('activiteitenlog')
        verbose_name_plural = _('activiteitenlogs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['status', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email if self.user else 'Anonymous'} - {self.action} - {self.timestamp}"