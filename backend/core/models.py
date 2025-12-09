from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class TimeStampedModel(models.Model):
    """
    Abstract base model met timestamps voor alle modellen.
    """
    
    # Unieke identificatie
    id = models.UUIDField(
        _('UUID'),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Unieke identificatie voor dit object')
    )
    
    # Timestamps voor tracking
    created_at = models.DateTimeField(
        _('aangemaakt op'),
        auto_now_add=True,
        help_text=_('Datum en tijd wanneer dit object aangemaakt is')
    )
    
    updated_at = models.DateTimeField(
        _('bijgewerkt op'),
        auto_now=True,
        help_text=_('Datum en tijd wanneer dit object voor het laatst bijgewerkt is')
    )
    
    # Metadata voor auditing
    created_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name=_('aangemaakt door'),
        help_text=_('Gebruiker die dit object aangemaakt heeft')
    )
    
    updated_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name=_('bijgewerkt door'),
        help_text=_('Gebruiker die dit object voor het laatst bijgewerkt heeft')
    )
    
    # Soft delete voor data retention
    is_deleted = models.BooleanField(
        _('verwijderd'),
        default=False,
        help_text=_('Indicatie of dit object zacht verwijderd is')
    )
    
    deleted_at = models.DateTimeField(
        _('verwijderd op'),
        null=True,
        blank=True,
        help_text=_('Datum en tijd wanneer dit object zacht verwijderd is')
    )
    
    # Audit logging
    version = models.PositiveIntegerField(
        _('versie'),
        default=1,
        help_text=_('Versienummer voor optimistic locking')
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['is_deleted']),
        ]
    
    def save(self, *args, **kwargs):
        """
        Override save method voor versie management en audit logging.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        request = kwargs.pop('request', None)
        
        # Set created_by/updated_by als request beschikbaar is
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if not self.pk:  # Object wordt aangemaakt
                if not self.created_by_id:
                    self.created_by = request.user
            else:  # Object wordt bijgewerkt
                self.updated_by = request.user
            
            # Increment versie voor optimistic locking
            if self.pk:
                self.version = models.F('version') + 1
        
        super().save(*args, **kwargs)
    
    def soft_delete(self, user=None):
        """
        Zachte verwijdering van het object.
        """
        from django.utils import timezone
        
        self.is_deleted = True
        self.deleted_at = timezone.now()
        
        if user:
            self.updated_by = user
        
        self.save()
    
    def restore(self, user=None):
        """
        Herstel zacht verwijderd object.
        """
        self.is_deleted = False
        self.deleted_at = None
        
        if user:
            self.updated_by = user
        
        self.save()
    
    def hard_delete(self, *args, **kwargs):
        """
        Harde verwijdering (override voor veiligheid).
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Log de verwijdering voor audit purposes
        logger.warning(
            f"Hard delete of {self.__class__.__name__} with ID {self.id}"
        )
        
        super().delete(*args, **kwargs)
    
    @property
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
            'id': str(self.id),
            'model': self.__class__.__name__,
            'created_at': self.created_at.isoformat() if self.created_at else None,
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
    Extended TimeStampedModel met soft delete manager.
    """
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Voor admin access tot alles
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """
        Override delete voor soft delete pattern.
        """
        self.soft_delete()
    
    def permanent_delete(self, *args, **kwargs):
        """
        Permanente verwijdering van database.
        """
        super(TimeStampedModel, self).delete(*args, **kwargs)