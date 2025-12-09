from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from .models import (
    Order, OrderItem, Payment, 
    OrderTag, OrderAttachment, OrderHistory
)


class OrderItemInline(admin.TabularInline):
    """
    Inline admin voor order items.
    """
    model = OrderItem
    extra = 0
    fields = ['line_number', 'item_type', 'description', 'quantity', 'unit', 'unit_price', 'is_delivered']
    readonly_fields = ['line_number']
    ordering = ['line_number']


class PaymentInline(admin.TabularInline):
    """
    Inline admin voor betalingen.
    """
    model = Payment
    extra = 0
    fields = ['payment_number', 'amount', 'payment_method', 'status', 'payment_date']
    readonly_fields = ['payment_number']


class OrderHistoryInline(admin.TabularInline):
    """
    Inline admin voor order geschiedenis.
    """
    model = OrderHistory
    extra = 0
    readonly_fields = ['action', 'old_value', 'new_value', 'changed_by', 'changed_at']
    can_delete = False
    max_num = 10


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface voor orders.
    """
    list_display = [
        'order_number', 'client', 'status_badge', 'priority_badge',
        'payment_status_badge', 'total_incl_tax_display', 
        'amount_due_display', 'delivery_date_display',
        'created_at', 'assigned_to_display'
    ]
    
    list_filter = [
        'status', 'priority', 'payment_status', 'client',
        'created_at', 'delivery_date', 'assigned_to', 'is_deleted'
    ]
    
    search_fields = [
        'order_number', 'reference', 'client__company_name',
        'client__email', 'tracking_number', 'internal_notes'
    ]
    
    readonly_fields = [
        'order_number', 'subtotal_excl_tax_display', 'tax_amount_display',
        'total_excl_tax_display', 'total_incl_tax_display',
        'amount_paid_display', 'amount_due_display', 'profit_margin_display',
        'is_paid', 'is_overdue', 'days_overdue', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (_('Identificatie'), {
            'fields': ('order_number', 'reference', 'quote')
        }),
        (_('Klant informatie'), {
            'fields': ('client', 'contact_person', 'assigned_to')
        }),
        (_('Status en workflow'), {
            'fields': ('status', 'priority', 'payment_status')
        }),
        (_('Financieel'), {
            'fields': (
                'currency', 'exchange_rate', 'tax_rate', 'tax_inclusive',
                'shipping_costs', 'subtotal_excl_tax_display', 'tax_amount_display',
                'total_excl_tax_display', 'total_incl_tax_display',
                'amount_paid_display', 'amount_due_display', 'profit_margin_display',
                'payment_method', 'payment_terms', 'payment_due_date',
                'is_paid', 'is_overdue', 'days_overdue'
            )
        }),
        (_('Levering'), {
            'fields': (
                'delivery_address', 'billing_address', 'delivery_date',
                'actual_delivery_date', 'shipping_method', 'tracking_number',
                'delivery_instructions'
            )
        }),
        (_('Documentatie'), {
            'fields': ('internal_notes', 'client_notes', 'terms_conditions')
        }),
        (_('Tracking'), {
            'fields': (
                'confirmed_at', 'processing_started_at', 'shipped_at',
                'delivered_at', 'cancelled_at', 'completed_at'
            )
        }),
        (_('Relaties'), {
            'fields': ('project', 'tags', 'attachments')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    inlines = [OrderItemInline, PaymentInline, OrderHistoryInline]
    
    actions = [
        'confirm_selected', 'start_processing_selected', 'mark_as_shipped_selected',
        'mark_as_delivered_selected', 'cancel_selected', 'complete_selected',
        'export_orders', 'send_invoice_reminder'
    ]
    
    def status_badge(self, obj):
        """Display status met kleurcodering"""
        colors = {
            'draft': 'gray',
            'pending': 'lightgray',
            'confirmed': 'blue',
            'processing': 'orange',
            'ready_for_shipment': 'lightblue',
            'shipped': 'purple',
            'delivered': 'green',
            'partially_delivered': 'lightgreen',
            'cancelled': 'red',
            'refunded': 'darkred',
            'completed': 'darkgreen'
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
    
    def payment_status_badge(self, obj):
        """Display betaalstatus met kleurcodering"""
        colors = {
            'pending': 'yellow',
            'partially_paid': 'lightblue',
            'paid': 'green',
            'overdue': 'red',
            'refunded': 'darkred',
            'failed': 'black'
        }
        
        color = colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_badge.short_description = _('Betaalstatus')
    
    def total_incl_tax_display(self, obj):
        """Display totaalprijs"""
        return f"€{obj.total_incl_tax:,.2f}"
    total_incl_tax_display.short_description = _('Totaal')
    
    def amount_due_display(self, obj):
        """Display nog te betalen bedrag"""
        amount_due = obj.amount_due
        if amount_due > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">€{:.2f}</span>',
                amount_due
            )
        return f"€{amount_due:,.2f}"
    amount_due_display.short_description = _('Nog te betalen')
    
    def delivery_date_display(self, obj):
        """Display leverdatum"""
        if obj.delivery_date:
            today = timezone.now().date()
            delivery_date = obj.delivery_date.date()
            
            if delivery_date < today and obj.status not in ['delivered', 'completed', 'cancelled']:
                return format_html(
                    '<span style="color: red; font-weight: bold;">{} (verlopen)</span>',
                    delivery_date.strftime('%d-%m-%Y')
                )
            elif delivery_date == today:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">{} (vandaag)</span>',
                    delivery_date.strftime('%d-%m-%Y')
                )
            
            return delivery_date.strftime('%d-%m-%Y')
        return "-"
    delivery_date_display.short_description = _('Leverdatum')
    
    def assigned_to_display(self, obj):
        """Display toegewezen medewerker"""
        return obj.assigned_to.email if obj.assigned_to else _('Niet toegewezen')
    assigned_to_display.short_description = _('Toegewezen aan')
    
    def subtotal_excl_tax_display(self, obj):
        """Display subtotaal"""
        return f"€{obj.subtotal_excl_tax:,.2f}"
    subtotal_excl_tax_display.short_description = _('Subtotaal excl. BTW')
    
    def tax_amount_display(self, obj):
        """Display BTW bedrag"""
        return f"€{obj.tax_amount:,.2f}"
    tax_amount_display.short_description = _('BTW bedrag')
    
    def total_excl_tax_display(self, obj):
        """Display totaal excl. BTW"""
        return f"€{obj.total_excl_tax:,.2f}"
    total_excl_tax_display.short_description = _('Totaal excl. BTW')
    
    def amount_paid_display(self, obj):
        """Display betaald bedrag"""
        return f"€{obj.amount_paid:,.2f}"
    amount_paid_display.short_description = _('Betaald')
    
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
    
    def confirm_selected(self, request, queryset):
        """Bevestig geselecteerde orders"""
        count = 0
        for order in queryset:
            if order.confirm():
                count += 1
        
        self.message_user(
            request,
            f"{count} orders bevestigd."
        )
    confirm_selected.short_description = _("Bevestig orders")
    
    def export_orders(self, request, queryset):
        """Exporteer orders naar CSV"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Client', 'Status', 'Total', 'Payment Status',
            'Delivery Date', 'Created', 'Items Count'
        ])
        
        for order in queryset:
            writer.writerow([
                order.order_number,
                str(order.client),
                order.get_status_display(),
                order.total_incl_tax,
                order.get_payment_status_display(),
                order.delivery_date.strftime('%Y-%m-%d') if order.delivery_date else '',
                order.created_at.strftime('%Y-%m-%d'),
                order.items.count()
            ])
        
        return response
    export_orders.short_description = _("Exporteer naar CSV")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin voor order items"""
    list_display = ['order', 'line_number', 'description', 'quantity', 'unit', 'unit_price', 'is_delivered']
    list_filter = ['item_type', 'is_delivered', 'order__status']
    search_fields = ['description', 'order__order_number', 'product__title', 'service__name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin voor betalingen"""
    list_display = ['payment_number', 'order', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['payment_number', 'order__order_number', 'transaction_id', 'payer_email']


# Registreer andere modellen
admin.site.register(OrderTag)
admin.site.register(OrderAttachment)
admin.site.register(OrderHistory)