from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    Client, ClientContact, Address, 
    ClientTag, ClientNote
)


class ClientContactInline(admin.TabularInline):
    """
    Inline admin voor klantcontacten.
    """
    model = ClientContact
    extra = 1
    fields = ['first_name', 'last_name', 'email', 'phone', 'job_title', 'is_primary', 'is_active']


class AddressInline(admin.TabularInline):
    """
    Inline admin voor adressen.
    """
    model = Address
    extra = 1
    fields = ['address_type', 'street', 'postal_code', 'city', 'country', 'is_primary', 'is_active']


class ClientNoteInline(admin.TabularInline):
    """
    Inline admin voor klantnotities.
    """
    model = ClientNote
    extra = 0
    readonly_fields = ['created_at', 'created_by']
    fields = ['title', 'note_type', 'privacy_level', 'is_pinned', 'created_at']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin interface voor klanten.
    """
    list_display = [
        'client_number', 'company_name', 'client_type_badge', 
        'status_badge', 'email', 'phone', 'assigned_to_display'
    ]
    
    list_filter = [
        'client_type', 'status', 'industry', 
        'assigned_to', 'created_at'
    ]
    
    search_fields = [
        'client_number', 'company_name', 'legal_name', 
        'email', 'phone', 'tax_number', 'chamber_of_commerce'
    ]
    
    readonly_fields = [
        'client_number', 'full_address_display',
        'is_active_client', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Identificatie'), {
            'fields': ('client_number', 'company_name', 'legal_name')
        }),
        (_('Type en status'), {
            'fields': ('client_type', 'status', 'assigned_to')
        }),
        (_('Contact informatie'), {
            'fields': ('email', 'phone', 'website')
        }),
        (_('Adres informatie'), {
            'fields': ('street', 'postal_code', 'city', 'country', 'full_address_display')
        }),
        (_('Zakelijke informatie'), {
            'fields': ('tax_number', 'chamber_of_commerce', 'industry')
        }),
        (_('Financiële informatie'), {
            'fields': ('credit_limit', 'payment_terms', 'currency')
        }),
        (_('Metadata'), {
            'fields': ('source', 'tags', 'internal_notes')
        }),
        (_('Tijdsaanduidingen'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    inlines = [ClientContactInline, AddressInline, ClientNoteInline]
    
    actions = ['activate_clients', 'deactivate_clients', 'export_clients']
    
    def client_type_badge(self, obj):
        """Display klanttype met kleurcodering"""
        colors = {
            'individual': 'blue',
            'business': 'green',
            'government': 'purple',
            'non_profit': 'orange',
            'partner': 'teal'
        }
        
        color = colors.get(obj.client_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_client_type_display()
        )
    client_type_badge.short_description = _('Type')
    
    def status_badge(self, obj):
        """Display status met kleurcodering"""
        colors = {
            'prospect': 'yellow',
            'active': 'green',
            'inactive': 'gray',
            'suspended': 'red',
            'former': 'darkgray'
        }
        
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    
    def assigned_to_display(self, obj):
        """Display toegewezen gebruiker"""
        return obj.assigned_to.email if obj.assigned_to else _('Niet toegewezen')
    assigned_to_display.short_description = _('Toegewezen aan')
    
    def full_address_display(self, obj):
        """Display volledig adres"""
        return obj.full_address or _('Geen adres opgegeven')
    full_address_display.short_description = _('Volledig adres')
    
    def activate_clients(self, request, queryset):
        """Activeer geselecteerde klanten"""
        count = queryset.update(status='active')
        self.message_user(
            request,
            f"{count} klanten geactiveerd."
        )
    activate_clients.short_description = _("Activeer klanten")
    
    def export_clients(self, request, queryset):
        """Exporteer klanten naar CSV"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="clients_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Client Number', 'Company Name', 'Email', 'Phone',
            'Type', 'Status', 'City', 'Country'
        ])
        
        for client in queryset:
            writer.writerow([
                client.client_number,
                client.company_name,
                client.email,
                client.phone,
                client.get_client_type_display(),
                client.get_status_display(),
                client.city,
                client.country
            ])
        
        return response
    export_clients.short_description = _("Exporteer naar CSV")


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    """Admin voor klantcontacten"""
    list_display = ['get_full_name', 'client', 'email', 'phone', 'job_title', 'is_primary', 'is_active']
    list_filter = ['is_primary', 'is_active', 'role', 'client']
    search_fields = ['first_name', 'last_name', 'email', 'client__company_name']
    
    def get_full_name(self, obj):
        return obj.full_name
    get_full_name.short_description = _('Naam')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin voor adressen"""
    list_display = ['client', 'address_type', 'city', 'country', 'is_primary', 'is_active']
    list_filter = ['address_type', 'country', 'is_primary', 'is_active']
    search_fields = ['street', 'city', 'client__company_name']


# Registreer andere modellen
admin.site.register(ClientTag)
admin.site.register(ClientNote)