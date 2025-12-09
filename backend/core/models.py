import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def get_short_name(self):
        return self.first_name

class SiteConfig(models.Model):
    company_name = models.CharField(max_length=200)
    company_email = models.EmailField()
    company_phone = models.CharField(max_length=20)
    company_address = models.TextField()
    
    # Social media
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    
    # Configuration
    maintenance_mode = models.BooleanField(default=False)
    allow_registration = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configuration'
    
    def __str__(self):
        return self.company_name
    



class TimeStampedModel(models.Model):
    """
    Abstract base model met timestamps voor alle modellen.

    id:
     not editable, it is unike, random uuid4 id
    """

    id = models.UUIDField(
        _('UUID'),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unieke identificatie voor dit object")
    )

    created_at = models.DateTimeField(
        _('aangemaakt op'),
        auto_now_add=True,
        help_text = _("Datum en tijd wanneer dit object aangemaakt is")
    )

    updated_at = models.DateTimeField(
        _("bijgewerkt op"),
        auto_now=True, # Bij elke save() wordt deze bijgewerkt
        help_text = _("Datum en tijd wanneer dit object voor het laatst bijgewerkt is.")
    )

    created_by = models.ForeignKey(
        "core.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        verbose_name=_("aangemaakt door"),
        help_text=_("gebruiker die dit object aangemaakt heeft")
    )

    updated_by = models.ForeignKey(
        "core.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        verbose_name=_("bijgewerkt door"),
        help_text=_("gebruiker die dit object voor het laatst bijgewerkt heeft")
    )


    is_deleted = models.BooleanField(
        _("verwijderd"),
        default=False,
        help_text=_("Indicatie of dit object zacht verwijderd is")
    )

    deleted_at = models.DateTimeField(
        _("verwijderd op"),
        null=True,
        blank=True,
        help_text=_("Datum en tijd wanneer dit object zacht verwijderd is")
    )

    version = models.PositiveIntegerField(
        _("versie"),
        default=1,
        help_text=_("versienummer voor optimistic locking")
    )

    ########################### Functions ###########################

    class Meta:
        abstract = True # Dit model wordt niet als aparte tabel aangemaakt
        ordering = ['-created_at'] # Standaard sorteren op aanmaakdatum, nieuwste eerst
        indexes = [ # Indexen voor betere performance bij queries
            models.Index(fields=['created_at']), # sorteren op aanmaakdatum
            models.Index(fields=['updated_at']),
            models.Index(fields=["is_deleted"])
        ]
    
    def save(self, *args, **kwargs):
        """
        Overschrijf de save methode om automatisch created_by en updated_by in te stellen.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        request = kwargs.pop("request", None)

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if not self.pk:# Nieuw object
                if not self.created_by_id: # Als created_by nog niet is ingesteld
                    self.created_by = request.user  # Stel created_by in
            else:
                self.updated_by = request.user  # Stel updated_by in

            # Increment versie voor optimistic locking
            if self.pk:
                self.version = models.F("version") + 1
            
        super().save(*args, **kwargs) # Roep de originele save methode aan. dit is belangrijk om oneindige recursie te voorkomen
    
    def soft_delete(self, user=None): 
        """
        zacht verwijderen van het object. Je kunt het object herstelen.
        dit fuc verwijdert het object nie maar zet het bij verwijdert section
        """
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()

        if user:
            self.updated_by = user
        
        self.save()

    def restore(self, user=None): 
        """
        Docstring for restore
        
        :param self: Description
        """

        self.is_deleted = False
        self.deleted_at = None

        if user:
            self.updated_by = user
        
        self.save()

    def hard_delete(self, *args, **kwargs):
        """
        Docstring for hard_delete
        
        :param self: Description
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.warning(
            f"Hard delete od {self.__class__.__name__} with ID {self.id}"
        )

        super().delete(*args, **kwargs)

    @property # maak er een property van zodat je het kunt aanroepen als een attribuut, zonder het hele class te hoeven aanroepen!
    def age(self): 
        """
        Leeftijd van het object in dagen.

        """
        from django.utils import timezone

        if self.created_at:
            delta = timezone.now() - self.created_at
            return delta.days
        return None
    
    @property 
    def last_modified_age(self):
        """
        Tijd sinds laatste wijziging in dagen.

        """
        from django.utils import timezone

        if self.updated_at:
            delta = timezone.now() - self.updated_at
            return delta.days
        return None


        
    def get_audit_log(self):
        """
        Genereer audit log entry voor dit object.

        """
        return {
            "id": str(self.id),
            "model": self.__class__.__name__,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by.email if self.created_by else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by.email if self.updated_by else None,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'version': self.version,
            'age_days': self.age,
            'last_modified_days': self.last_modified_age
        }



class SoftDeleteManager(models.Manager):
    """
    Custom manager voor soft delete functionaliteit.

    """
    

    def get_queryset(self):
        """
        Standaard queryset die zacht verwijderde items uitsluit.

        """
        return super().get_queryset().filter(is_deleted=False)
    def all_with_deleted(self):
        """
        Retourneer alle items inclusief zacht verwijderde.

        """
        return super().get_queryset()
    def deleted_only(self):
        """
        Retourneer alleen zacht verwijderde items.
        """
        return super().get_queryset().filter(is_deleted=True)
    def active_only(self):
        """
        Retourneer alleen actieve (niet verwijderde) items.
        """
        return self.get_queryset()


class TimeStampedModelWithSoftDelete(TimeStampedModel):
    """
    Docstring for TimeStampedModelWithSoftDelete
    """

    objects = SoftDeleteManager()
    all_objects = models.Manager() # Voor admin access tot alles

    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """
        Override delete voor soft delete pattern.
        """
        self.soft_delete()
    
    def permanent_delete(self, *args, **kwargs):
        """
        Permanent verwijdering van database.
        """
        super(TimeStampedModel, self).delete(*args, **kwargs)

