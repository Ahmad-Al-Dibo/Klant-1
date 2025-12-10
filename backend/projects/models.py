
from decimal import Decimal
from django.conf import settings
from django.db import models
from core.models import TimeStampedModelWithSoftDelete
from django.utils.translation import gettext_lazy as _  # Dit is de belangrijke import!

from core.validators import (
    MinValueValidator,
)

class Task(models.Model):
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='tasks',  # hiermee kun je project.tasks gebruiken
        verbose_name=_('project')
    )
    name = models.CharField(_('naam'), max_length=200)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=(
            ('pending', _('In afwachting')),
            ('in_progress', _('Bezig')),
            ('completed', _('Voltooid')),
        ),
        default='pending'
    )
    due_date = models.DateField(_('vervaldatum'), null=True, blank=True)
    
    def __str__(self):
        return self.name

class ProjectStatus(models.TextChoices):
    """
    Status keuzes voor projecten.
    """
    DRAFT = 'draft', _('Concept')
    PLANNING = 'planning', _('In planning')
    ACTIVE = 'active', _('Actief')
    ON_HOLD = 'on_hold', _('Gepauzeerd')
    COMPLETED = 'completed', _('Voltooid')
    CANCELLED = 'cancelled', _('Geannuleerd')
    ARCHIVED = 'archived', _('Gearchiveerd')

class ProjectPriority(models.TextChoices):
    """
    Prioriteitsniveaus voor projecten.
    """
    LOW = 'low', _('Laag')
    MEDIUM = 'medium', _('Medium')
    HIGH = 'high', _('Hoog')
    URGENT = 'urgent', _('Urgent')


class Project(TimeStampedModelWithSoftDelete):
    """
    Hoofdmodel voor projecten.
    
    TECHNISCHE CONCEPTEN:
    - Project management met milestones
    - Team assignment en resource planning
    - Budget tracking
    - Timeline management
    """
    
    # Identificatie
    project_number = models.CharField(
        _('projectnummer'),
        max_length=50,
        unique=True,
        editable=False,
        help_text=_('Uniek projectnummer gegenereerd door het systeem')
    )
    
    name = models.CharField(
        _('projectnaam'),
        max_length=200,
        help_text=_('Naam van het project')
    )

    
    description = models.TextField(
        _('beschrijving'),
        blank=True,
        help_text=_('Gedetailleerde beschrijving van het project')
    )
    
    # Status en prioriteit
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
        help_text=_('Huidige status van het project')
    )
    
    priority = models.CharField(
        _('prioriteit'),
        max_length=20,
        choices=ProjectPriority.choices,
        default=ProjectPriority.MEDIUM,
        help_text=_('Prioriteit van het project')
    )
    
    # # Klant en team
    # client = models.ForeignKey(
    #     'clients.Client',
    #     on_delete=models.PROTECT,
    #     related_name='projects',
    #     verbose_name=_('klant'),
    #     help_text=_('Klant voor wie het project wordt uitgevoerd')
    # )
    client = models.TextField(default=None)
    
    # contact_person = models.ForeignKey(
    #     'clients.ClientContact',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='projects',
    #     verbose_name=_('contactpersoon'),
    #     help_text=_('Contactpersoon bij de klant')
    # )
    contact_person = models.TextField(default=None)
    
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects',
        verbose_name=_('projectmanager'),
        help_text=_('Projectmanager verantwoordelijk voor dit project')
    )
    
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='projects',
        verbose_name=_('teamleden'),
        help_text=_('Teamleden die aan dit project werken')
    )
    
    # Tijdlijn
    start_date = models.DateField(
        _('startdatum'),
        null=True,
        blank=True,
        help_text=_('Geplande startdatum van het project')
    )
    
    end_date = models.DateField(
        _('einddatum'),
        null=True,
        blank=True,
        help_text=_('Geplande einddatum van het project')
    )
    
    actual_start_date = models.DateField(
        _('werkelijke startdatum'),
        null=True,
        blank=True,
        help_text=_('Werkelijke startdatum van het project')
    )
    
    actual_end_date = models.DateField(
        _('werkelijke einddatum'),
        null=True,
        blank=True,
        help_text=_('Werkelijke einddatum van het project')
    )
    
    # Budget
    budget = models.DecimalField(
        _('budget'),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0, message=_('Budget mag niet negatief zijn.'))],
        help_text=_('Totaal budget voor het project')
    )
    
    currency = models.CharField(
        _('valuta'),
        max_length=3,
        default='EUR',
        help_text=_('Valuta voor budget en kosten')
    )
    
    # Notities en documentatie
    internal_notes = models.TextField(
        _('interne notities'),
        blank=True,
        help_text=_('Interne notities over het project')
    )
    
    client_notes = models.TextField(
        _('klantnotities'),
        blank=True,
        help_text=_('Notities voor de klant')
    )
    
    requirements = models.TextField(
        _('vereisten'),
        blank=True,
        help_text=_('Projectvereisten en specificaties')
    )
    
    # Metadata
    tags = models.ManyToManyField(
        'ProjectTag',
        blank=True,
        related_name='projects',
        verbose_name=_('tags'),
        help_text=_('Tags voor categorisatie')
    )
    
    category = models.ForeignKey(
        'ProjectCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name=_('categorie'),
        help_text=_('Categorie van het project')
    )
    
    # Tracking
    completed_at = models.DateTimeField(
        _('voltooid op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer het project is voltooid')
    )
    
    cancelled_at = models.DateTimeField(
        _('geannuleerd op'),
        null=True,
        blank=True,
        help_text=_('Datum/tijd wanneer het project is geannuleerd')
    )

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projecten")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['project_number']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['project_manager', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.project_number} - {self.name}"
    
    def save(self, *args, **kwargs):
        """
        
        """
        if not self.project_number:
            self.project_number = self.generate_project_number()
        super().save(*args, **kwargs)
    
    def generate_project_number(self):
        from django.utils import timezone
        import random
        import string

        year = timezone.now().strftime("%y")
        sequential = Project.objects.filter(
            project_number__startswith=f"PRJ{year}"
        ).count() + 1

        random_suffix = ''.join(random.choices(string.ascii_uppercase, k=2))

        return f"PRJ{year}{sequential:04d}{random_suffix}"
    
    @property
    def duration_days(self):
        """Projectduur in dagen"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None
    
    @property
    def actual_duration_days(self):
        """Werkelijke projectduur in dagen"""
        if self.actual_start_date and self.actual_end_date:
            return (self.actual_end_date - self.actual_start_date).days
        return None
    
    @property
    def progress_percentage(self):
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='completed').count()
        return int((completed_tasks / total_tasks) * 100)
    
    @property
    def total_costs(self):
        """Totale projectkosten"""
        # TODO: Implement cost calculation
        return Decimal('0.00')
    
    @property
    def budget_utilization(self):
        """Budget gebruik percentage"""
        if self.budget > 0:
            return (self.total_costs / self.budget) * 100
        return 0
    
    @property
    def is_active(self):
        """Is het project actief?"""
        return self.status == ProjectStatus.ACTIVE
    
    @property
    def is_overdue(self):
        """Is het project achter op schema?"""
        from django.utils import timezone
        
        if self.end_date and self.status == ProjectStatus.ACTIVE:
            return timezone.now().date() > self.end_date
        return False
    

class ProjectCategory(models.Model):
    """
    Categorieën voor projecten.
    """
    name = models.CharField(
        _('naam'),
        max_length=100,
        unique=True,
        help_text=_('Naam van de categorie')
    )
    
    slug = models.SlugField(
        _('slug'),
        max_length=110,
        unique=True,
        help_text=_('URL-vriendelijke naam')
    )
    
    description = models.TextField(
        _('beschrijving'),
        blank=True,
        help_text=_('Beschrijving van de categorie')
    )
    
    icon = models.CharField(
        _('icoon'),
        max_length=50,
        blank=True,
        help_text=_('FontAwesome icon class (bijv. fa-building)')
    )
    
    color = models.CharField(
        _('kleur'),
        max_length=7,
        default='#3498db',
        help_text=_('Hex kleurcode voor visualisatie')
    )
    
    is_active = models.BooleanField(
        _('actief'),
        default=True,
        help_text=_('Of deze categorie beschikbaar is voor gebruik')
    )

    class Meta:
        verbose_name = _('project categorie')
        verbose_name_plural = _('project categorieën')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-genereren van slug"""
        from django.utils.text import slugify
        
        if not self.slug:
            self.slug = slugify(self.name) # creating url-vriendelijk name.
        super().save(*args, **kwargs)



class ProjectTag(models.Model):
    """
    Tags voor project categorisatie.
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
        verbose_name = _('project tag')
        verbose_name_plural = _('project tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-genereren van slug"""
        from django.utils.text import slugify
        
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)