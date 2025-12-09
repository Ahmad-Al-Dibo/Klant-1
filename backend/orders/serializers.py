from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal

from .models import (
    Order, OrderItem, Payment, 
    OrderTag, OrderAttachment, OrderHistory
)
from clients.serializers import ClientSerializer, ClientContactSerializer, AddressSerializer
from quotes.serializers import QuoteSerializer
from authentication.serializers import UserSerializer


class OrderTagSerializer(serializers.ModelSerializer):
    """
    Serializer voor order tags.
    """
    
    class Meta:
        model = OrderTag
        fields = ['id', 'name', 'slug', 'color', 'description', 'is_active']
        read_only_fields = ['slug']


class OrderAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer voor order bijlagen.
    """
    
    file_size_display = serializers.SerializerMethodField()
    file_extension = serializers.CharField(read_only=True)
    
    class Meta:
        model = OrderAttachment
        fields = [
            'id', 'name', 'file', 'file_type', 'file_size',
            'file_size_display', 'file_extension', 'attachment_type',
            'uploaded_by', 'uploaded_at', 'description'
        ]
        read_only_fields = [
            'file_type', 'file_size', 'file_size_display',
            'file_extension', 'uploaded_by', 'uploaded_at'
        ]
    
    def get_file_size_display(self, obj):
        """Formatteer bestandsgrootte"""
        if obj.file_size:
            size = obj.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return None
    
    def validate_file(self, value):
        """Valideer geüpload bestand"""
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                _('Bestand mag niet groter zijn dan 10MB')
            )
        
        allowed_types = [
            'application/pdf',
            'image/jpeg', 'image/png', 'image/gif',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'text/csv',
        ]
        
        import magic
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(value.read(1024))
        value.seek(0)  # Reset file pointer
        
        if file_type not in allowed_types:
            raise serializers.ValidationError(
                _('Bestandstype niet toegestaan. Toegestane types: PDF, JPG, PNG, GIF, DOC, DOCX, XLS, XLSX, TXT, CSV')
            )
        
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer voor order items.
    """
    
    subtotal_excl_tax = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_incl_tax = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    remaining_quantity = serializers.DecimalField(max_digits=10, decimal_places=3, read_only=True)
    is_fully_delivered = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'line_number', 'item_type', 'product', 'service',
            'description', 'specification', 'quantity', 'unit',
            'unit_price', 'cost_price', 'discount_percentage',
            'tax_rate', 'stock_location', 'batch_number',
            'serial_number', 'is_delivered', 'delivered_quantity',
            'delivery_date', 'notes', 'subtotal_excl_tax',
            'tax_amount', 'total_incl_tax', 'profit', 'profit_margin',
            'remaining_quantity', 'is_fully_delivered'
        ]
        read_only_fields = ['is_delivered', 'delivered_quantity', 'delivery_date']
    
    def validate(self, attrs):
        """Valideer order item"""
        # Valideer dat of product of service is opgegeven
        if not attrs.get('product') and not attrs.get('service'):
            raise serializers.ValidationError(
                _('Of product of dienst moet worden opgegeven')
            )
        
        # Valideer hoeveelheid
        if attrs.get('quantity', 0) <= 0:
            raise serializers.ValidationError({
                'quantity': _('Hoeveelheid moet groter zijn dan 0')
            })
        
        # Valideer eenheidsprijs
        if attrs.get('unit_price', 0) <= 0:
            raise serializers.ValidationError({
                'unit_price': _('Eenheidsprijs moet groter zijn dan 0')
            })
        
        return attrs


class OrderItemCreateSerializer(OrderItemSerializer):
    """
    Serializer voor het aanmaken van order items.
    """
    
    product_slug = serializers.SlugField(write_only=True, required=False)
    service_slug = serializers.SlugField(write_only=True, required=False)
    
    class Meta(OrderItemSerializer.Meta):
        fields = OrderItemSerializer.Meta.fields + ['product_slug', 'service_slug']
    
    def validate(self, attrs):
        """Verwerk product/service slugs"""
        product_slug = attrs.pop('product_slug', None)
        service_slug = attrs.pop('service_slug', None)
        
        if product_slug:
            try:
                from products.models import Product
                product = Product.objects.get(slug=product_slug, is_active=True)
                attrs['product'] = product
                attrs['description'] = attrs.get('description', product.title)
                attrs['unit_price'] = attrs.get('unit_price', product.price)
            except Product.DoesNotExist:
                raise serializers.ValidationError({
                    'product_slug': _('Product niet gevonden')
                })
        
        if service_slug:
            try:
                from services.models import Service
                service = Service.objects.get(slug=service_slug, is_active=True)
                attrs['service'] = service
                attrs['description'] = attrs.get('description', service.name)
                attrs['unit_price'] = attrs.get('unit_price', service.price or 0)
            except Service.DoesNotExist:
                raise serializers.ValidationError({
                    'service_slug': _('Dienst niet gevonden')
                })
        
        return super().validate(attrs)


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer voor betalingen.
    """
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'order', 'amount', 'currency',
            'payment_method', 'status', 'transaction_id',
            'payment_date', 'received_date', 'payer_name',
            'payer_email', 'notes', 'receipt', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['payment_number', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Valideer betaling"""
        order = attrs.get('order') or self.instance.order if self.instance else None
        
        if order:
            # Valideer dat betaling niet meer is dan openstaand bedrag
            amount = attrs.get('amount', 0)
            if amount > order.amount_due:
                raise serializers.ValidationError({
                    'amount': _('Betaling kan niet meer zijn dan openstaand bedrag')
                })
        
        return attrs


class OrderHistorySerializer(serializers.ModelSerializer):
    """
    Serializer voor order geschiedenis.
    """
    
    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = OrderHistory
        fields = [
            'id', 'order', 'action', 'old_value', 'new_value',
            'changed_fields', 'changed_by', 'changed_by_email',
            'changed_by_name', 'changed_at', 'ip_address',
            'user_agent', 'notes'
        ]
        read_only_fields = ['changed_at']


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer voor order lijst weergave.
    """
    
    client = ClientSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    total_incl_tax = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    amount_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'client', 'status', 'status_display',
            'priority', 'priority_display', 'payment_status', 'payment_status_display',
            'total_incl_tax', 'amount_paid', 'amount_due', 'is_paid',
            'is_overdue', 'days_overdue', 'delivery_date', 'created_at'
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer voor gedetailleerde order weergave.
    """
    
    client = ClientSerializer(read_only=True)
    contact_person = ClientContactSerializer(read_only=True)
    quote = QuoteSerializer(read_only=True)
    delivery_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    tags = OrderTagSerializer(many=True, read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    attachments = OrderAttachmentSerializer(many=True, read_only=True)
    history = OrderHistorySerializer(many=True, read_only=True)
    
    # Calculated fields
    subtotal_excl_tax = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_excl_tax = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_incl_tax = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    amount_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    
    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            # Identificatie
            'id', 'order_number', 'reference', 'quote',
            
            # Klant informatie
            'client', 'contact_person',
            
            # Status
            'status', 'status_display', 'priority', 'priority_display',
            'payment_status', 'payment_status_display', 'payment_method', 'payment_method_display',
            
            # Financieel
            'currency', 'exchange_rate', 'tax_rate', 'tax_inclusive',
            'subtotal_excl_tax', 'tax_amount', 'total_excl_tax', 'total_incl_tax',
            'amount_paid', 'amount_due', 'profit_margin', 'is_paid', 'is_overdue', 'days_overdue',
            'payment_terms', 'payment_due_date',
            
            # Levering
            'delivery_address', 'billing_address', 'delivery_date', 'actual_delivery_date',
            'shipping_method', 'tracking_number', 'shipping_costs', 'delivery_instructions',
            
            # Items en betalingen
            'items', 'payments',
            
            # Documentatie
            'internal_notes', 'client_notes', 'terms_conditions',
            
            # Tracking
            'confirmed_at', 'processing_started_at', 'shipped_at',
            'delivered_at', 'cancelled_at', 'completed_at',
            
            # Relaties
            'project', 'assigned_to', 'tags', 'attachments', 'history',
            
            # Metadata
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'order_number', 'created_at', 'updated_at',
            'confirmed_at', 'processing_started_at', 'shipped_at',
            'delivered_at', 'cancelled_at', 'completed_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer voor het aanmaken van orders.
    """
    
    items = OrderItemCreateSerializer(many=True, required=False)
    quote_id = serializers.UUIDField(write_only=True, required=False)
    client_id = serializers.UUIDField(write_only=True, required=True)
    
    class Meta:
        model = Order
        fields = [
            'reference', 'quote_id', 'client_id', 'contact_person',
            'priority', 'currency', 'exchange_rate', 'tax_rate',
            'tax_inclusive', 'payment_method', 'payment_terms',
            'payment_due_date', 'delivery_address', 'billing_address',
            'delivery_date', 'shipping_method', 'shipping_costs',
            'internal_notes', 'client_notes', 'terms_conditions',
            'delivery_instructions', 'project', 'assigned_to',
            'tags', 'items'
        ]
    
    def validate(self, attrs):
        """Valideer order creatie"""
        quote_id = attrs.pop('quote_id', None)
        client_id = attrs.pop('client_id', None)
        
        # Valideer client
        try:
            from clients.models import Client
            client = Client.objects.get(id=client_id)
            attrs['client'] = client
        except Client.DoesNotExist:
            raise serializers.ValidationError({
                'client_id': _('Klant niet gevonden')
            })
        
        # Valideer quote als opgegeven
        if quote_id:
            try:
                from quotes.models import Quote
                quote = Quote.objects.get(id=quote_id, client=client)
                attrs['quote'] = quote
                
                # Kopieer gegevens van quote
                if not attrs.get('delivery_address') and quote.delivery_address:
                    attrs['delivery_address'] = quote.delivery_address
                if not attrs.get('billing_address') and quote.billing_address:
                    attrs['billing_address'] = quote.billing_address
                if not attrs.get('contact_person') and quote.contact_person:
                    attrs['contact_person'] = quote.contact_person
                if not attrs.get('delivery_date') and quote.delivery_date:
                    attrs['delivery_date'] = quote.delivery_date
                
            except Quote.DoesNotExist:
                raise serializers.ValidationError({
                    'quote_id': _('Offerte niet gevonden of behoort niet tot deze klant')
                })
        
        return attrs
    
    def create(self, validated_data):
        """Creëer order met items"""
        items_data = validated_data.pop('items', [])
        tags = validated_data.pop('tags', [])
        
        # Creëer order
        order = Order.objects.create(**validated_data)
        
        # Voeg tags toe
        order.tags.set(tags)
        
        # Creëer items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer voor het updaten van orders.
    """
    
    class Meta:
        model = Order
        fields = [
            'status', 'priority', 'payment_status', 'payment_method',
            'payment_terms', 'payment_due_date', 'delivery_address',
            'billing_address', 'delivery_date', 'actual_delivery_date',
            'shipping_method', 'tracking_number', 'shipping_costs',
            'internal_notes', 'client_notes', 'delivery_instructions',
            'project', 'assigned_to', 'tags'
        ]
    
    def validate(self, attrs):
        """Valideer order updates"""
        instance = self.instance
        
        # Valideer status transities
        new_status = attrs.get('status')
        if new_status and instance:
            valid_transitions = {
                'draft': ['confirmed', 'cancelled'],
                'confirmed': ['processing', 'cancelled'],
                'processing': ['ready_for_shipment', 'cancelled'],
                'ready_for_shipment': ['shipped', 'cancelled'],
                'shipped': ['delivered', 'partially_delivered', 'cancelled'],
                'delivered': ['completed', 'cancelled'],
                'partially_delivered': ['delivered', 'cancelled'],
                'cancelled': [],  # Geen transitie mogelijk
                'refunded': [],  # Geen transitie mogelijk
                'completed': [],  # Geen transitie mogelijk
            }
            
            if instance.status in valid_transitions:
                if new_status not in valid_transitions[instance.status]:
                    raise serializers.ValidationError({
                        'status': _('Ongeldige status transitie')
                    })
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update order met logging"""
        # Log wijzigingen
        changes = []
        for field, new_value in validated_data.items():
            old_value = getattr(instance, field)
            if old_value != new_value:
                if field == 'status':
                    old_display = dict(OrderStatus.choices).get(old_value, old_value)
                    new_display = dict(OrderStatus.choices).get(new_value, new_value)
                    changes.append(f"Status gewijzigd van {old_display} naar {new_display}")
                elif field == 'assigned_to':
                    old_name = old_value.get_full_name() if old_value else 'Niemand'
                    new_name = new_value.get_full_name() if new_value else 'Niemand'
                    changes.append(f"Toegewezen aan gewijzigd van {old_name} naar {new_name}")
        
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Log geschiedenis
        if changes:
            OrderHistory.objects.create(
                order=instance,
                action='updated',
                changed_fields=list(validated_data.keys()),
                changed_by=self.context['request'].user,
                notes='; '.join(changes)
            )
        
        return instance