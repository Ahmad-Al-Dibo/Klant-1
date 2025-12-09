from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from .models import (
    Quote, QuoteItem, QuoteTag, 
    QuoteAttachment, QuoteTemplate, QuoteHistory
)


class QuoteItemInline(admin.TabularInline):
    """
    Inline admin voor offerte items.
    """
    model = QuoteItem
    extra = 1
    fields = ['line_number', 'item_type', 'description', 'quantity', 'unit', 'unit_price', 'discount_percentage']
    readonly_fields = ['line_number']


class QuoteHistoryInline(admin.TabularInline):
    """
    Inline admin voor offerte geschiedenis.
    """
    model = QuoteHistory
    extra = 0
    readonly_fields = ['action', 'old_value', 'new_value', 'changed_by', 'changed_at']
    can_delete = False
    max_num = 10


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    """
    Admin interface voor offertes.
    """
    list_display = [
        'quote_number', 'client', 'status_badge', 'priority_badge',
        'total_incl_tax_display', 'days_until_expiry_display',
        'created_at', 'sent_at'
    ]
    
    list_filter = [
        'status', 'priority', 'client', 'created_at', 
        'sent_at', 'valid_until', 'is_deleted'
    ]
    
    search_fields = [
        'quote_number', 'client__name', 'client__email',
        'reference', 'internal_notes'
    ]
    
    readonly_fields = [
        'quote_number', 'subtotal_excl_tax_display', 'tax_amount_display',
        'total_incl_tax_display', 'profit_margin_display', 'is_expired',
        'days_until_expiry', 'is_convertible', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Identificatie'), {
            'fields': ('quote_number', 'reference', 'revision', 'parent_quote')
        }),
        (_('Klant informatie'), {
            'fields': ('client', 'contact_person')
        }),
        (_('Status en workflow'), {
            'fields': ('status', 'priority', 'converted_to_order')
        }),
        (_('Financieel'), {
            'fields': (
                'currency', 'exchange_rate', 'tax_rate', 'tax_inclusive',
                'subtotal_excl_tax_display', 'tax_amount_display', 
                'total_incl_tax_display', 'profit_margin_display'
            )
        }),
        (_('Geldigheid'), {
            'fields': ('valid_from', 'valid_until', 'is_expired', 'days_until_expiry')
        }),
        (_('Levering en betaling'), {
            'fields': (
                'delivery_address', 'billing_address', 'delivery_date',
                'payment_terms', 'delivery_terms'
            )
        }),
        (_('Documentatie'), {
            'fields': ('internal_notes', 'client_notes', 'terms_conditions')
        }),
        (_('Tracking'), {
            'fields': (
                'sent_at', 'viewed_at', 'responded_at', 
                'accepted_at', 'expired_at'
            )
        }),
        (_('Metadata'), {
            'fields': ('tags', 'attachments', 'created_at', 'updated_at')
        }),
    )
    
    inlines = [QuoteItemInline, QuoteHistoryInline]
    
    actions = [
        'mark_as_sent', 'mark_as_accepted', 'mark_as_rejected',
        'create_revision', 'export_quotes', 'send_reminder'
    ]
    
    def status_badge(self, obj):
        """Display status met kleurcodering"""
        colors = {
            'draft': 'gray',
            'pending': 'orange',
            'sent': 'blue',
            'viewed': 'lightblue',
            'negotiation': 'purple',
            'accepted': 'green',
            'rejected': 'red',
            'expired': 'darkgray',
            'cancelled': 'black',
            'converted': 'darkgreen'
        }
        
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    
    def priority_badge(self, obj):
        """Display prioriteit met kleurcodering"""
        colors = {
            'low': 'gray',
            'medium': 'orange',
            'high': 'red',
            'urgent': 'darkred'
        }
        
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = _('Prioriteit')
    
    def total_incl_tax_display(self, obj):
        """Formatteer totaalprijs"""
        return f"€{obj.total_incl_tax:,.2f}"
    total_incl_tax_display.short_description = _('Totaal')
    
    def days_until_expiry_display(self, obj):
        """Dagen tot vervaldatum met waarschuwing"""
        days = obj.days_until_expiry
        if days is None:
            return "-"
        
        if days < 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">Verlopen</span>'
            )
        elif days < 3:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{} dagen</span>',
                days
            )
        else:
            return f"{days} dagen"
    days_until_expiry_display.short_description = _('Verloopt over')
    
    def subtotal_excl_tax_display(self, obj):
        """Display subtotaal"""
        return f"€{obj.subtotal_excl_tax:,.2f}"
    subtotal_excl_tax_display.short_description = _('Subtotaal excl. BTW')
    
    def tax_amount_display(self, obj):
        """Display BTW bedrag"""
        return f"€{obj.tax_amount:,.2f}"
    tax_amount_display.short_description = _('BTW bedrag')
    
    def profit_margin_display(self, obj):
        """Display winstmarge"""
        margin = obj.profit_margin
        if margin >= 30:
            color = 'green'
        elif margin >= 15:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, f"{margin:.1f}"
        )
    profit_margin_display.short_description = _('Winstmarge')
    
    def mark_as_sent(self, request, queryset):
        """Markeer geselecteerde offertes als verzonden"""
        for quote in queryset:
            quote.send_to_client()
        
        self.message_user(
            request,
            f"{queryset.count()} offertes gemarkeerd als verzonden."
        )
    mark_as_sent.short_description = _("Markeer als verzonden")
    
    def create_revision(self, request, queryset):
        """Maak revisie van geselecteerde offertes"""
        count = 0
        for quote in queryset:
            new_quote = quote.create_revision()
            count += 1
        
        self.message_user(
            request,
            f"{count} revisies aangemaakt."
        )
    create_revision.short_description = _("Maak revisie")
    
    def export_quotes(self, request, queryset):
        """Exporteer offertes naar CSV"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="quotes_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Quote Number', 'Client', 'Status', 'Total', 'Created', 
            'Valid Until', 'Items Count'
        ])
        
        for quote in queryset:
            writer.writerow([
                quote.quote_number,
                str(quote.client),
                quote.get_status_display(),
                quote.total_incl_tax,
                quote.created_at.strftime('%Y-%m-%d'),
                quote.valid_until.strftime('%Y-%m-%d') if quote.valid_until else '',
                quote.items.count()
            ])
        
        return response
    export_quotes.short_description = _("Exporteer naar CSV")


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    """Admin voor offerte items"""
    list_display = ['quote', 'line_number', 'description', 'quantity', 'unit_price', 'total_incl_tax_display']
    list_filter = ['item_type', 'quote__status']
    search_fields = ['description', 'quote__quote_number']
    
    def total_incl_tax_display(self, obj):
        return f"€{obj.total_incl_tax:,.2f}"
    total_incl_tax_display.short_description = _('Totaal')


@admin.register(QuoteTemplate)
class QuoteTemplateAdmin(admin.ModelAdmin):
    """Admin voor offerte templates"""
    list_display = ['name', 'is_active', 'default_validity_days', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


# Registreer andere modellen
admin.site.register(QuoteTag)
admin.site.register(QuoteAttachment)
admin.site.register(QuoteHistory)