from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Project, ProjectCategory, ProjectTag, ProjectStatus, ProjectPriority, Task
from .forms import ProjectTagForm

User = get_user_model()


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin configuratie voor Task.
    """
    list_display = ('name', 'project', 'status', 'due_date')
    search_fields = ('name', 'description', 'project__name', 'assigned_to__email')
    list_filter = ('status', 'due_date')
    ordering = ('-due_date',)
    autocomplete_fields = ('project',)



@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuratie voor ProjectCategory.
    """
    list_display = ('name', 'slug', 'color_display', 'is_active', 'project_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    list_editable = ('is_active',)
    readonly_fields = ('color_display',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'is_active')
        }),
        (_('Weergave'), {
            'fields': ('icon', 'color', 'color_display')
        }),
        (_('Beschrijving'), {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )
    
    def color_display(self, obj):
        """
        Toon kleur als gekleurd blokje.
        """
        if obj.color:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; '
                'background-color: {}; border: 1px solid #ccc; border-radius: 3px;" '
                'title="{}"></span>',
                obj.color,
                obj.color
            )
        return '-'
    color_display.short_description = _('kleur')
    color_display.admin_order_field = 'color'
    
    def project_count(self, obj):
        """
        Aantal projecten in deze categorie.
        """
        return obj.projects.count()
    project_count.short_description = _('aantal projecten')






@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    """
    Admin configuratie voor ProjectTag.
    """
    form = ProjectTagForm
    list_display = ('name', 'slug', 'color_display', 'is_active', 'project_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    list_editable = ('is_active',)
    readonly_fields = ('color_display',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'is_active')
        }),
        (_('Weergave'), {
            'fields': ('color', 'color_display')
        }),
        (_('Beschrijving'), {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )
    
    def color_display(self, obj):
        """
        Toon kleur als gekleurd blokje.
        """
        if obj.color:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; '
                'background-color: {}; border: 1px solid #ccc; border-radius: 3px;" '
                'title="{}"></span>',
                obj.color,
                obj.color
            )
        return '-'
    color_display.short_description = _('kleur')
    color_display.admin_order_field = 'color'
    
    def project_count(self, obj):
        """
        Aantal projecten met deze tag.
        """
        return obj.projects.count()
    project_count.short_description = _('aantal projecten')


class TeamMembersInline(admin.TabularInline):
    """
    Inline voor team members in Project admin.
    """
    model = Project.team_members.through
    extra = 1
    verbose_name = _('team lid')
    verbose_name_plural = _('team leden')
    
    # Let op: het veld in de through tabel is afhankelijk van de naam van de relatie
    # Meestal is het 'user' of 'member' - controleer je gegenereerde through tabel
    # Voor nu verwijderen we autocomplete_fields tot we de juiste naam weten
    # autocomplete_fields = ('user',)  # Commented out - foutoplossing


class TagsInline(admin.TabularInline):
    """
    Inline voor tags in Project admin.
    """
    model = Project.tags.through
    extra = 1
    verbose_name = _('tag')
    verbose_name_plural = _('tags')
    # autocomplete_fields = ('projecttag',)  # Commented out - mogelijke fout


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin configuratie voor Project.
    """
    list_display = (
        'project_number',
        'name',
        'client_display',
        'status_display',
        'priority_display',
        'project_manager_display',
        'start_date',
        'end_date',
        'budget_display',
        'progress_percentage_display',
        'is_overdue_display'
    )
    
    list_filter = (
        'status',
        'priority',
        ('start_date', admin.DateFieldListFilter),
        ('end_date', admin.DateFieldListFilter),
        ('project_manager', admin.RelatedOnlyFieldListFilter),
        'category',
    )
    
    search_fields = (
        'project_number',
        'name',
        'description',
        'client',
        'contact_person',
    )
    
    ordering = ('-created_at',)
    
    # Corrigeer: 'modified_at' komt van TimeStampedModelWithSoftDelete
    # We moeten controleren of deze velden bestaan in het model
    readonly_fields = (
        'project_number',
        'created_at',
        'updated_at',  # Gewijzigd van 'modified_at' naar 'updated_at'
        'deleted_at',
        'completed_at',
        'cancelled_at',
        'duration_days_display',
        'actual_duration_days_display',
        'progress_percentage_display',
        'total_costs_display',
        'budget_utilization_display',
        'is_active_display',
        'is_overdue_display',
    )
    
    fieldsets = (
        (_('Basis informatie'), {
            'fields': (
                'project_number',
                'name',
                'description',
                'category',
            )
        }),
        
        (_('Status en prioriteit'), {
            'fields': (
                'status',
                'priority',
                'is_active_display',
                'is_overdue_display',
            )
        }),
        
        (_('Klant en team'), {
            'fields': (
                'client',
                'contact_person',
                'project_manager',
                # 'team_members_display',  # Removed - veroorzaakt mogelijk problemen
            )
        }),
        
        (_('Tijdlijn'), {
            'fields': (
                'start_date',
                'end_date',
                'duration_days_display',
                'actual_start_date',
                'actual_end_date',
                'actual_duration_days_display',
            )
        }),
        
        (_('Budget'), {
            'fields': (
                'budget',
                'currency',
                'total_costs_display',
                'budget_utilization_display',
            )
        }),
        
        (_('Voortgang'), {
            'fields': (
                'progress_percentage_display',
                'completed_at',
                'cancelled_at',
            )
        }),
        
        (_('Notities'), {
            'fields': (
                'internal_notes',
                'client_notes',
                'requirements',
            ),
            'classes': ('collapse',)
        }),
        
        (_('Metadata'), {
            'fields': (
                'tags',  # Direct veld gebruiken in plaats van custom display
                'created_at',
                'updated_at',  # Gewijzigd van 'modified_at' naar 'updated_at'
                'deleted_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('tags', 'team_members')
    
    inlines = [TeamMembersInline]
    
    autocomplete_fields = ('project_manager', 'category')
    
    actions = ['mark_as_active', 'mark_as_completed', 'mark_as_cancelled']
    
    def get_queryset(self, request):
        """
        Exclude soft-deleted items by default.
        """
        qs = super().get_queryset(request)
        return qs.filter(deleted_at__isnull=True)
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Dynamisch formulier aanpassen.
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Filter alleen actieve gebruikers voor team members en project manager
        user_field = form.base_fields.get('project_manager')
        if user_field:
            user_field.queryset = User.objects.filter(is_active=True)
        
        team_members_field = form.base_fields.get('team_members')
        if team_members_field:
            team_members_field.queryset = User.objects.filter(is_active=True)
        
        return form
    
    # Custom display methods voor list_display
    def client_display(self, obj):
        """
        Toon klant (ingekort als te lang).
        """
        if obj.client and len(obj.client) > 20:
            return f"{obj.client[:20]}..."
        return obj.client or '-'
    client_display.short_description = _('klant')
    client_display.admin_order_field = 'client'
    
    def status_display(self, obj):
        """
        Toon status met kleurcodering.
        """
        status_colors = {
            'draft': '#6c757d',      # Grijs
            'planning': '#17a2b8',   # Cyan
            'active': '#28a745',     # Groen
            'on_hold': '#ffc107',    # Geel
            'completed': '#007bff',  # Blauw
            'cancelled': '#dc3545',  # Rood
            'archived': '#6c757d',   # Grijs
        }
        
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="display: inline-block; padding: 2px 8px; '
            'border-radius: 12px; background-color: {}; color: white; '
            'font-size: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = _('status')
    status_display.admin_order_field = 'status'
    
    def priority_display(self, obj):
        """
        Toon prioriteit met kleurcodering.
        """
        priority_colors = {
            'low': '#28a745',     # Groen
            'medium': '#ffc107',  # Geel
            'high': '#fd7e14',    # Oranje
            'urgent': '#dc3545',  # Rood
        }
        
        color = priority_colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="display: inline-block; padding: 2px 8px; '
            'border-radius: 12px; background-color: {}; color: white; '
            'font-size: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_display.short_description = _('prioriteit')
    priority_display.admin_order_field = 'priority'
    
    def project_manager_display(self, obj):
        """
        Toon project manager.
        """
        if obj.project_manager:
            return obj.project_manager.get_full_name() or obj.project_manager.email
        return '-'
    project_manager_display.short_description = _('project manager')
    project_manager_display.admin_order_field = 'project_manager'
    
    def budget_display(self, obj):
        """
        Toon budget geformatteerd.
        """
        return f"{obj.currency} {obj.budget:,.2f}"
    budget_display.short_description = _('budget')
    budget_display.admin_order_field = 'budget'
    
    def progress_percentage_display(self, obj):
        """
        Toon voortgang als progress bar.
        """
        progress = obj.progress_percentage
        color = '#28a745' if progress >= 80 else '#ffc107' if progress >= 50 else '#dc3545'
        
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<div style="flex: 1; height: 10px; background-color: #e9ecef; '
            'border-radius: 5px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background-color: {};"></div>'
            '</div>'
            '<span style="font-size: 12px; font-weight: bold;">{}%</span>'
            '</div>',
            progress,
            color,
            int(progress)
        )
    progress_percentage_display.short_description = _('voortgang')
    
    def is_overdue_display(self, obj):
        """
        Toon of project achter loopt.
        """
        if obj.is_overdue:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✓</span>'
            )
        return format_html(
            '<span style="color: #28a745;">-</span>'
        )
    is_overdue_display.short_description = _('achter')
    is_overdue_display.admin_order_field = 'end_date'
    
    # Custom display methods voor fieldsets
    def duration_days_display(self, obj):
        """
        Toon projectduur.
        """
        if obj.duration_days is not None:
            return f"{obj.duration_days} dagen"
        return '-'
    duration_days_display.short_description = _('geplande duur')
    
    def actual_duration_days_display(self, obj):
        """
        Toon werkelijke projectduur.
        """
        if obj.actual_duration_days is not None:
            return f"{obj.actual_duration_days} dagen"
        return '-'
    actual_duration_days_display.short_description = _('werkelijke duur')
    
    def total_costs_display(self, obj):
        """
        Toon totale kosten.
        """
        return f"{obj.currency} {obj.total_costs:,.2f}"
    total_costs_display.short_description = _('totale kosten')
    
    def budget_utilization_display(self, obj):
        """
        Toon budget gebruik.
        """
        utilization = obj.budget_utilization
        color = '#dc3545' if utilization > 100 else '#28a745' if utilization <= 80 else '#ffc107'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            int(utilization)
        )
    budget_utilization_display.short_description = _('budget gebruik')
    
    def is_active_display(self, obj):
        """
        Toon of project actief is.
        """
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Actief</span>'
            )
        return format_html(
            '<span style="color: #6c757d;">✗ Niet actief</span>'
        )
    is_active_display.short_description = _('actief')
    
    # Admin actions
    def mark_as_active(self, request, queryset):
        """
        Markeer geselecteerde projecten als actief.
        """
        updated = queryset.update(status=ProjectStatus.ACTIVE)
        self.message_user(
            request,
            _('{} project(en) gemarkeerd als actief.').format(updated)
        )
    mark_as_active.short_description = _('Markeer als actief')
    
    def mark_as_completed(self, request, queryset):
        """
        Markeer geselecteerde projecten als voltooid.
        """
        from django.utils import timezone
        
        updated = queryset.update(
            status=ProjectStatus.COMPLETED,
            completed_at=timezone.now()
        )
        self.message_user(
            request,
            _('{} project(en) gemarkeerd als voltooid.').format(updated)
        )
    mark_as_completed.short_description = _('Markeer als voltooid')
    
    def mark_as_cancelled(self, request, queryset):
        """
        Markeer geselecteerde projecten als geannuleerd.
        """
        from django.utils import timezone
        
        updated = queryset.update(
            status=ProjectStatus.CANCELLED,
            cancelled_at=timezone.now()
        )
        self.message_user(
            request,
            _('{} project(en) gemarkeerd als geannuleerd.').format(updated)
        )
    mark_as_cancelled.short_description = _('Markeer als geannuleerd')