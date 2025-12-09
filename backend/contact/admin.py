from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from .models import (
    ContactCategory, 
    ContactMessage, 
    ContactAttachment,
    NewsletterSubscriber
)


@admin.register(ContactCategory)
class ContactCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface voor contactcategorieën.
    
    TECHNISCHE CONCEPTEN:
    - List display customisatie
    - Inline editing
    - Hierarchische weergave
    """
    
    list_display = ['name', 'slug', 'category_type', 'priority', 'is_active', 'message_count']
    list_filter = ['category_type', 'is_active', 'parent']
    search_fields = ['name', 'description', 'email_recipient']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['priority', 'name']
    
    fieldsets = (
        (_('Basis informatie'), {
            'fields': ('name', 'slug', 'category_type', 'description', 'parent')
        }),
        (_('Configuratie'), {
            'fields': ('email_recipient', 'priority', 'is_active')
        }),
    )
    
    def message_count(self, obj):
        """Aantal berichten in deze categorie"""
        return obj.messages.count()
    message_count.short_description = _('Aantal berichten')


class ContactAttachmentInline(admin.TabularInline):
    """
    Inline admin voor bijlagen.
    
    TECHNISCHE CONCEPTEN:
    - TabularInline voor compacte weergave
    - Read-only fields voor metadata
    """
    
    model = ContactAttachment
    extra = 0
    readonly_fields = ['file_name', 'file_type', 'file_size', 'uploaded_at', 'is_safe']
    fields = ['file', 'file_name', 'file_type', 'file_size', 'is_safe']
    
    def has_add_permission(self, request, obj=None):
        """Alleen toevoegen bij nieuwe berichten"""
        return obj is None
    
    def has_change_permission(self, request, obj=None):
        """Geen wijzigingen toestaan"""
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin interface voor contactberichten.
    
    TECHNISCHE CONCEPTEN:
    - Advanced list display
    - Action bulk operations
    - State transition management
    """
    
    list_display = [
        'reference_number', 'full_name', 'email', 'category',
        'subject', 'status', 'priority_display', 'assigned_to',
        'created_at', 'response_time_display'
    ]
    
    list_filter = [
        'status', 'priority', 'category', 'assigned_to',
        'created_at', 'responded_at'
    ]
    
    search_fields = [
        'reference_number', 'full_name', 'email', 'company_name',
        'subject', 'message'
    ]
    
    readonly_fields = [
        'uuid', 'reference_number', 'ip_address', 'user_agent',
        'created_at', 'updated_at', 'response_time_display'
    ]
    
    fieldsets = (
        (_('Identificatie'), {
            'fields': ('uuid', 'reference_number')
        }),
        (_('Verzender informatie'), {
            'fields': ('full_name', 'email', 'phone_number', 'company_name')
        }),
        (_('Bericht inhoud'), {
            'fields': ('category', 'subject', 'message')
        }),
        (_('Status en workflow'), {
            'fields': ('status', 'priority', 'assigned_to', 'response_notes')
        }),
        (_('Tracking'), {
            'fields': ('ip_address', 'user_agent', 'page_url')
        }),
        (_('Gerelateerde items'), {
            'fields': ('related_product', 'related_service', 'related_quote')
        }),
        (_('Tijdsaanduidingen'), {
            'fields': ('created_at', 'updated_at', 'responded_at', 'response_time_display')
        }),
    )
    
    inlines = [ContactAttachmentInline]
    
    actions = [
        'mark_as_read', 'mark_as_in_progress', 'mark_as_resolved',
        'assign_to_me', 'export_selected'
    ]
    
    def priority_display(self, obj):
        """Display prioriteit met kleurcodering"""
        if obj.priority <= 3:
            color = 'red'
        elif obj.priority <= 6:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.priority
        )
    priority_display.short_description = _('Prioriteit')
    priority_display.admin_order_field = 'priority'
    
    def response_time_display(self, obj):
        """Display response tijd"""
        if obj.response_time:
            total_seconds = obj.response_time.total_seconds()
            
            if total_seconds < 3600:
                return f"{int(total_seconds / 60)} min"
            elif total_seconds < 86400:
                return f"{int(total_seconds / 3600)} uur"
            else:
                return f"{int(total_seconds / 86400)} dagen"
        return "-"
    response_time_display.short_description = _('Response tijd')
    
    def mark_as_read(self, request, queryset):
        """Markeer geselecteerde berichten als gelezen"""
        count = queryset.update(status='read')
        self.message_user(
            request,
            f"{count} berichten gemarkeerd als gelezen."
        )
    mark_as_read.short_description = _("Markeer als gelezen")
    
    def mark_as_in_progress(self, request, queryset):
        """Markeer geselecteerde berichten als in behandeling"""
        count = queryset.update(status='in_progress')
        self.message_user(
            request,
            f"{count} berichten gemarkeerd als in behandeling."
        )
    mark_as_in_progress.short_description = _("Markeer als in behandeling")
    
    def mark_as_resolved(self, request, queryset):
        """Markeer geselecteerde berichten als afgehandeld"""
        count = queryset.update(
            status='resolved',
            responded_at=timezone.now()
        )
        self.message_user(
            request,
            f"{count} berichten gemarkeerd als afgehandeld."
        )
    mark_as_resolved.short_description = _("Markeer als afgehandeld")
    
    def assign_to_me(self, request, queryset):
        """Wijs geselecteerde berichten toe aan huidige gebruiker"""
        count = queryset.update(
            assigned_to=request.user,
            status='in_progress'
        )
        self.message_user(
            request,
            f"{count} berichten toegewezen aan jou."
        )
    assign_to_me.short_description = _("Wijs toe aan mij")
    
    def export_selected(self, request, queryset):
        """Export geselecteerde berichten naar CSV"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_messages.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Reference', 'Name', 'Email', 'Category', 'Subject',
            'Status', 'Priority', 'Created', 'Responded'
        ])
        
        for message in queryset:
            writer.writerow([
                message.reference_number,
                message.full_name,
                message.email,
                message.category.name if message.category else '',
                message.subject,
                message.get_status_display(),
                message.priority,
                message.created_at.strftime('%Y-%m-%d %H:%M'),
                message.responded_at.strftime('%Y-%m-%d %H:%M') if message.responded_at else ''
            ])
        
        return response
    export_selected.short_description = _("Exporteer naar CSV")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """
    Admin interface voor nieuwsbrief inschrijvingen.
    
    TECHNISCHE CONCEPTEN:
    - Subscription management
    - GDPR compliance tools
    - Export functionaliteit
    """
    
    list_display = [
        'email', 'full_name', 'is_confirmed', 'is_active',
        'confirmed_at', 'created_at'
    ]
    
    list_filter = [
        'is_confirmed', 'is_active', 'confirmed_at', 'created_at'
    ]
    
    search_fields = ['email', 'full_name']
    
    readonly_fields = [
        'subscription_token', 'unsubscribe_token',
        'ip_address', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Inschrijving informatie'), {
            'fields': ('email', 'full_name', 'subscription_preferences')
        }),
        (_('Status'), {
            'fields': ('is_confirmed', 'confirmed_at', 'is_active', 'unsubscribed_at')
        }),
        (_('Technische details'), {
            'fields': ('subscription_token', 'unsubscribe_token', 'ip_address')
        }),
        (_('Tijdsaanduidingen'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['resend_confirmation', 'export_subscribers']
    
    def resend_confirmation(self, request, queryset):
        """Stuur bevestigingsmail opnieuw"""
        from .signals import send_subscription_confirmation
        
        for subscriber in queryset.filter(is_confirmed=False):
            send_subscription_confirmation(subscriber)
        
        self.message_user(
            request,
            f"Bevestigingsmails opnieuw verstuurd naar {queryset.count()} inschrijvers."
        )
    resend_confirmation.short_description = _("Stuur bevestiging opnieuw")
    
    def export_subscribers(self, request, queryset):
        """Export geselecteerde inschrijvingen naar CSV"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter_subscribers.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Email', 'Name', 'Confirmed', 'Active',
            'Subscribed At', 'Confirmed At'
        ])
        
        for subscriber in queryset:
            writer.writerow([
                subscriber.email,
                subscriber.full_name or '',
                'Yes' if subscriber.is_confirmed else 'No',
                'Yes' if subscriber.is_active else 'No',
                subscriber.created_at.strftime('%Y-%m-%d %H:%M'),
                subscriber.confirmed_at.strftime('%Y-%m-%d %H:%M') if subscriber.confirmed_at else ''
            ])
        
        return response
    export_subscribers.short_description = _("Exporteer naar CSV")