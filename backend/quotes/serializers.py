from rest_framework import serializers
from django.contrib.auth.models import User
from quotes.models import Quote, QuoteItem, QuoteDocument
from clients.models import Client, ClientContact
from django.utils import timezone


class QuoteItemSerializer(serializers.ModelSerializer):
    """Serializer for QuoteItem model"""
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = QuoteItem
        fields = [
            'id', 'quote', 'description', 'quantity', 'unit_price',
            'tax_rate', 'discount_percentage', 'total', 'notes',
            'position', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total(self, obj):
        """Calculate item total with tax and discount"""
        subtotal = obj.quantity * obj.unit_price
        discount = subtotal * (obj.discount_percentage / 100) if obj.discount_percentage else 0
        taxed_amount = (subtotal - discount) * (obj.tax_rate / 100) if obj.tax_rate else 0
        return subtotal - discount + taxed_amount


class QuoteDocumentSerializer(serializers.ModelSerializer):
    """Serializer for QuoteDocument model"""
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()
    
    class Meta:
        model = QuoteDocument
        fields = [
            'id', 'quote', 'document_type', 'file',
            'file_url', 'file_name', 'file_size', 'file_type', 'file_extension',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        """Get absolute file URL"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_name(self, obj):
        """Get original file name"""
        if obj.file:
            return os.path.basename(obj.file.name)
        return None
    
    def get_file_size(self, obj):
        """Get file size in human readable format"""
        if obj.file and obj.file.size:
            size = obj.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.1f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):.1f} GB"
        return "0 B"
    
    def get_file_type(self, obj):
        """Get file MIME type based on extension"""
        if obj.file:
            filename = obj.file.name.lower()
            if filename.endswith('.pdf'):
                return 'PDF Document'
            elif filename.endswith(('.doc', '.docx')):
                return 'Word Document'
            elif filename.endswith(('.xls', '.xlsx')):
                return 'Excel Document'
            elif filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return 'Image'
            elif filename.endswith('.txt'):
                return 'Text File'
            else:
                return 'Document'
        return 'Unknown'
    
    def get_file_extension(self, obj):
        """Get file extension"""
        if obj.file:
            filename = obj.file.name
            return os.path.splitext(filename)[1].lower()
        return ''
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size too large. Maximum size is {max_size / (1024*1024)}MB."
            )
        
        # Check file extensions
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.txt']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value
    
    def validate_document_type(self, value):
        """Validate document type"""
        valid_types = ['quote', 'contract', 'attachment', 'other']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid document type. Must be one of: {', '.join(valid_types)}"
            )
        return value
    
    def create(self, validated_data):
        """Create document with proper naming"""
        request = self.context.get('request')
        quote = validated_data.get('quote')
        
        # If no custom filename, generate one
        if 'file' in validated_data and quote:
            original_filename = validated_data['file'].name
            ext = os.path.splitext(original_filename)[1]
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"quote_{quote.quote_number}_{timestamp}{ext}"
            validated_data['file'].name = new_filename
        
        document = QuoteDocument.objects.create(**validated_data)
        
        # Update quote's updated_at timestamp
        quote.updated_at = timezone.now()
        if request and request.user:
            quote.updated_by = request.user
        quote.save()
        
        return document
    
    def update(self, instance, validated_data):
        """Update document"""
        request = self.context.get('request')
        quote = instance.quote
        
        # If new file uploaded, rename it
        if 'file' in validated_data and validated_data['file'] != instance.file:
            original_filename = validated_data['file'].name
            ext = os.path.splitext(original_filename)[1]
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"quote_{quote.quote_number}_{timestamp}{ext}"
            validated_data['file'].name = new_filename
            
            # Delete old file
            if instance.file:
                instance.file.delete(save=False)
        
        # Update document
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Update quote's updated_at timestamp
        quote.updated_at = timezone.now()
        if request and request.user:
            quote.updated_by = request.user
        quote.save()
        
        return instance

class QuoteSerializer(serializers.ModelSerializer):
    """Serializer for Quote model"""
    items = QuoteItemSerializer(many=True, read_only=True)
    documents = QuoteDocumentSerializer(many=True, read_only=True)
    client_details = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    total_tax = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    validity_days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Quote
        fields = [
            'id', 'quote_number', 'client', 'contact', 'client_details', 'contact_details',
            'title', 'description', 'status', 'status_display',
            'issue_date', 'expiry_date', 'validity_days_remaining',
            'payment_terms', 'delivery_terms', 'notes',
            'subtotal', 'total_tax', 'total_discount', 'total_amount',
            'currency', 'language', 'template',
            'is_sent', 'sent_date', 'is_viewed', 'viewed_date',
            'accepted_date', 'rejected_date', 'rejection_reason',
            'created_by', 'updated_by', 'created_at', 'updated_at',
            'items', 'documents'
        ]
        read_only_fields = [
            'id', 'quote_number', 'created_at', 'updated_at',
            'is_sent', 'sent_date', 'is_viewed', 'viewed_date',
            'accepted_date', 'rejected_date', 'created_by', 'updated_by'
        ]
    
    def get_client_details(self, obj):
        """Get client details"""
        if obj.client:
            return {
                'id': obj.client.id,
                'name': obj.client.name,
                'company_name': obj.client.company_name,
                'email': obj.client.email,
                'phone': obj.client.phone
            }
        return None
    
    def get_contact_details(self, obj):
        """Get contact details"""
        if obj.contact:
            return {
                'id': obj.contact.id,
                'name': f"{obj.contact.first_name} {obj.contact.last_name}",
                'email': obj.contact.email,
                'phone': obj.contact.phone
            }
        return None
    
    def get_subtotal(self, obj):
        """Calculate quote subtotal"""
        subtotal = sum(item.quantity * item.unit_price for item in obj.items.all())
        return subtotal
    
    def get_total_tax(self, obj):
        """Calculate total tax"""
        total_tax = 0
        for item in obj.items.all():
            subtotal = item.quantity * item.unit_price
            discount = subtotal * (item.discount_percentage / 100) if item.discount_percentage else 0
            taxed_amount = (subtotal - discount) * (item.tax_rate / 100) if item.tax_rate else 0
            total_tax += taxed_amount
        return total_tax
    
    def get_total_discount(self, obj):
        """Calculate total discount"""
        total_discount = 0
        for item in obj.items.all():
            subtotal = item.quantity * item.unit_price
            discount = subtotal * (item.discount_percentage / 100) if item.discount_percentage else 0
            total_discount += discount
        return total_discount
    
    def get_total_amount(self, obj):
        """Calculate total amount"""
        subtotal = self.get_subtotal(obj)
        total_tax = self.get_total_tax(obj)
        total_discount = self.get_total_discount(obj)
        return subtotal - total_discount + total_tax
    
    def get_validity_days_remaining(self, obj):
        """Calculate days remaining until expiry"""
        if obj.expiry_date:
            today = timezone.now().date()
            if obj.expiry_date >= today:
                return (obj.expiry_date - today).days
            return 0
        return None
    
    def validate(self, data):
        """Validate quote data"""
        # Ensure expiry date is after issue date
        if data.get('expiry_date') and data.get('issue_date'):
            if data['expiry_date'] <= data['issue_date']:
                raise serializers.ValidationError({
                    'expiry_date': 'Expiry date must be after issue date'
                })
        
        # Ensure contact belongs to client
        if data.get('contact') and data.get('client'):
            if data['contact'].client != data['client']:
                raise serializers.ValidationError({
                    'contact': 'Contact must belong to the selected client'
                })
        
        return data
    
    def create(self, validated_data):
        """Create quote with generated quote number"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        # Generate quote number
        year = timezone.now().year
        last_quote = Quote.objects.filter(
            quote_number__startswith=f"Q{year}-"
        ).order_by('-quote_number').first()
        
        if last_quote:
            last_number = int(last_quote.quote_number.split('-')[1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        validated_data['quote_number'] = f"Q{year}-{new_number:04d}"
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update quote"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class QuoteListSerializer(serializers.ModelSerializer):
    """Simplified serializer for quote lists"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    contact_name = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Quote
        fields = [
            'id', 'quote_number', 'client', 'client_name',
            'contact_name', 'title', 'status', 'status_display',
            'issue_date', 'expiry_date', 'total_amount',
            'is_sent', 'is_viewed', 'created_at'
        ]
    
    def get_contact_name(self, obj):
        """Get contact full name"""
        if obj.contact:
            return f"{obj.contact.first_name} {obj.contact.last_name}"
        return None
    
    def get_total_amount(self, obj):
        """Calculate total amount"""
        total = 0
        for item in obj.items.all():
            subtotal = item.quantity * item.unit_price
            discount = subtotal * (item.discount_percentage / 100) if item.discount_percentage else 0
            taxed_amount = (subtotal - discount) * (item.tax_rate / 100) if item.tax_rate else 0
            total += subtotal - discount + taxed_amount
        return total


class QuoteExportSerializer(serializers.ModelSerializer):
    """Serializer for quote data export"""
    items = QuoteItemSerializer(many=True, read_only=True)
    client_details = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    totals = serializers.SerializerMethodField()
    
    class Meta:
        model = Quote
        fields = [
            'id', 'quote_number', 'client_details', 'contact_details',
            'title', 'description', 'status',
            'issue_date', 'expiry_date',
            'payment_terms', 'delivery_terms', 'notes',
            'currency', 'language',
            'is_sent', 'sent_date', 'is_viewed', 'viewed_date',
            'accepted_date', 'rejected_date', 'rejection_reason',
            'created_at', 'updated_at',
            'items', 'totals'
        ]
    
    def get_client_details(self, obj):
        if obj.client:
            return {
                'name': obj.client.name,
                'company_name': obj.client.company_name,
                'email': obj.client.email,
                'phone': obj.client.phone
            }
        return None
    
    def get_contact_details(self, obj):
        if obj.contact:
            return {
                'name': f"{obj.contact.first_name} {obj.contact.last_name}",
                'email': obj.contact.email,
                'phone': obj.contact.phone
            }
        return None
    
    def get_totals(self, obj):
        """Calculate all totals"""
        subtotal = 0
        total_tax = 0
        total_discount = 0
        
        for item in obj.items.all():
            item_subtotal = item.quantity * item.unit_price
            subtotal += item_subtotal
            
            discount = item_subtotal * (item.discount_percentage / 100) if item.discount_percentage else 0
            total_discount += discount
            
            taxed_amount = (item_subtotal - discount) * (item.tax_rate / 100) if item.tax_rate else 0
            total_tax += taxed_amount
        
        total_amount = subtotal - total_discount + total_tax
        
        return {
            'subtotal': subtotal,
            'total_tax': total_tax,
            'total_discount': total_discount,
            'total_amount': total_amount
        }
    


from rest_framework import serializers
from django.contrib.auth.models import User
from quotes.models import Quote, QuoteItem, QuoteDocument
from clients.models import Client, ClientContact
from django.utils import timezone
import os




class QuoteDocumentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for document lists"""
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    uploaded_by = serializers.SerializerMethodField()
    
    class Meta:
        model = QuoteDocument
        fields = [
            'id', 'document_type', 'file_name', 'file_size',
            'uploaded_by', 'created_at'
        ]
    
    def get_file_name(self, obj):
        if obj.file:
            return os.path.basename(obj.file.name)
        return None
    
    def get_file_size(self, obj):
        if obj.file and obj.file.size:
            return f"{obj.file.size / 1024:.0f} KB"
        return "0 KB"
    
    def get_uploaded_by(self, obj):
        # Assuming you have created_by field in your model
        if hasattr(obj, 'created_by') and obj.created_by:
            return obj.created_by.username
        return None


class QuoteDocumentDownloadSerializer(serializers.Serializer):
    """Serializer for document download information"""
    document_id = serializers.IntegerField()
    download_url = serializers.SerializerMethodField()
    
    def get_download_url(self, obj):
        """Generate download URL"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                f"/api/quotes/documents/{obj['document_id']}/download/"
            )
        return None