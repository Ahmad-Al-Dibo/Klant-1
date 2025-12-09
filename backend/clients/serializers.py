from rest_framework import serializers
from django.contrib.auth.models import User
from clients.models import Client, ClientContact, Address
from django.utils import timezone


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model"""
    class Meta:
        model = Address
        fields = [
            'id', 'street', 'house_number', 'addition', 
            'postal_code', 'city', 'country', 'address_type',
            'is_primary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_postal_code(self, value):
        """Validate postal code format"""
        if value:
            # Remove spaces and convert to uppercase
            value = value.replace(' ', '').upper()
            # Basic validation for Dutch postal codes (e.g., 1234AB)
            if len(value) != 6:
                raise serializers.ValidationError("Postal code must be 6 characters (e.g., 1234AB)")
            if not value[:4].isdigit():
                raise serializers.ValidationError("First 4 characters must be digits")
            if not value[4:].isalpha():
                raise serializers.ValidationError("Last 2 characters must be letters")
        return value


class ClientContactSerializer(serializers.ModelSerializer):
    """Serializer for ClientContact model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientContact
        fields = [
            'id', 'client', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'mobile', 'position', 'department',
            'is_primary_contact', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """Get full name of contact"""
        return f"{obj.first_name} {obj.last_name}"
    
    def validate_email(self, value):
        """Validate email uniqueness for this client"""
        if value:
            client_id = self.context.get('client_id') or (self.instance.client.id if self.instance else None)
            if client_id:
                existing = ClientContact.objects.filter(
                    client_id=client_id, 
                    email=value
                ).exclude(pk=self.instance.pk if self.instance else None)
                if existing.exists():
                    raise serializers.ValidationError("A contact with this email already exists for this client.")
        return value


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model"""
    contacts = ClientContactSerializer(many=True, read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    primary_contact = serializers.SerializerMethodField()
    primary_address = serializers.SerializerMethodField()
    quote_count = serializers.SerializerMethodField()
    active_quote_count = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'company_name', 'email', 'phone', 'website',
            'vat_number', 'registration_number', 'industry', 'client_type',
            'status', 'notes', 'payment_terms', 'credit_limit', 
            'discount_percentage', 'is_active', 'created_at', 'updated_at',
            'contacts', 'addresses', 'primary_contact', 'primary_address',
            'quote_count', 'active_quote_count', 'total_revenue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_primary_contact(self, obj):
        """Get primary contact details"""
        primary = obj.contacts.filter(is_primary_contact=True).first()
        if primary:
            return {
                'id': primary.id,
                'name': f"{primary.first_name} {primary.last_name}",
                'email': primary.email,
                'phone': primary.phone
            }
        return None
    
    def get_primary_address(self, obj):
        """Get primary address details"""
        primary = obj.addresses.filter(is_primary=True).first()
        if primary:
            return AddressSerializer(primary).data
        return None
    
    def get_quote_count(self, obj):
        """Get total number of quotes for this client"""
        return obj.quotes.count()
    
    def get_active_quote_count(self, obj):
        """Get number of active quotes for this client"""
        return obj.quotes.filter(status__in=['draft', 'sent', 'negotiating']).count()
    
    def get_total_revenue(self, obj):
        """Get total revenue from accepted quotes"""
        from quotes.models import Quote  # Import here to avoid circular import
        accepted_quotes = obj.quotes.filter(status='accepted')
        total = sum(quote.total_amount for quote in accepted_quotes if quote.total_amount)
        return total
    
    def validate_vat_number(self, value):
        """Validate VAT number format"""
        if value:
            # Basic VAT number validation (can be expanded based on country)
            value = value.replace(' ', '').upper()
            # Example: NL123456789B01
            if len(value) < 5:
                raise serializers.ValidationError("VAT number is too short")
        return value
    
    def create(self, validated_data):
        """Create client with default primary contact"""
        client = Client.objects.create(**validated_data)
        
        # Create default primary contact if email is provided
        if validated_data.get('email'):
            ClientContact.objects.create(
                client=client,
                first_name=validated_data.get('name', '').split()[0] if validated_data.get('name') else '',
                last_name=' '.join(validated_data.get('name', '').split()[1:]) if validated_data.get('name') else '',
                email=validated_data.get('email'),
                phone=validated_data.get('phone'),
                is_primary_contact=True
            )
        
        return client


class ClientListSerializer(serializers.ModelSerializer):
    """Simplified serializer for client lists"""
    primary_contact = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'company_name', 'email', 'phone',
            'client_type', 'status', 'is_active', 'created_at',
            'primary_contact'
        ]
    
    def get_primary_contact(self, obj):
        primary = obj.contacts.filter(is_primary_contact=True).first()
        if primary:
            return f"{primary.first_name} {primary.last_name}"
        return None


class ClientExportSerializer(serializers.ModelSerializer):
    """Serializer for client data export"""
    contacts = ClientContactSerializer(many=True, read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'company_name', 'email', 'phone', 'website',
            'vat_number', 'registration_number', 'industry', 'client_type',
            'status', 'notes', 'payment_terms', 'credit_limit',
            'discount_percentage', 'is_active', 'created_at',
            'contacts', 'addresses'
        ]