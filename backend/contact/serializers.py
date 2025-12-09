from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    ContactCategory, 
    ContactMessage, 
    ContactAttachment,
    NewsletterSubscriber
)

User = get_user_model()


class ContactCategorySerializer(serializers.ModelSerializer):
    """
    Serializer voor contactcategorieën.
    
    TECHNISCHE CONCEPTEN:
    - Read-only fields voor statistieken
    - Nested serialization voor subcategorieën
    - Slug auto-generatie
    """
    
    message_count = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactCategory
        fields = [
            'id', 'name', 'slug', 'category_type', 'description',
            'email_recipient', 'is_active', 'priority', 'parent',
            'message_count', 'subcategories'
        ]
        read_only_fields = ['slug', 'message_count', 'subcategories']
    
    def get_message_count(self, obj):
        """Aantal berichten in deze categorie"""
        return obj.messages.count()
    
    def get_subcategories(self, obj):
        """Recursieve subcategorie serialisatie"""
        subcategories = obj.subcategories.filter(is_active=True)
        return ContactCategorySerializer(subcategories, many=True).data
    
    def validate_name(self, value):
        """Valideer categorie naam"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                _('Naam moet minimaal 2 karakters bevatten')
            )
        return value.strip()
    
    def validate_email_recipient(self, value):
        """Valideer e-mail ontvanger"""
        if value:
            validator = EmailValidator()
            validator(value)
        return value


class ContactAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer voor contactbijlagen.
    
    TECHNISCHE CONCEPTEN:
    - File validatie in serializer
    - Read-only fields voor metadata
    - File size formatting
    """
    
    file_size_display = serializers.SerializerMethodField()
    is_image = serializers.BooleanField(read_only=True)
    file_extension = serializers.CharField(read_only=True)
    
    class Meta:
        model = ContactAttachment
        fields = [
            'id', 'file', 'file_name', 'file_type', 'file_size',
            'file_size_display', 'is_image', 'file_extension',
            'uploaded_at', 'is_safe'
        ]
        read_only_fields = [
            'file_name', 'file_type', 'file_size', 'file_size_display',
            'is_image', 'file_extension', 'uploaded_at', 'is_safe'
        ]
    
    def get_file_size_display(self, obj):
        """Formatteer bestandsgrootte voor display"""
        if obj.file_size:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if obj.file_size < 1024.0:
                    return f"{obj.file_size:.1f} {unit}"
                obj.file_size /= 1024.0
        return None
    
    def validate_file(self, value):
        """Valideer geüpload bestand"""
        # Controleer bestandsgrootte (10MB limit)
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                _('Bestand mag niet groter zijn dan 10MB')
            )
        
        # Controleer bestandstype
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif',
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ]
        
        import magic
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(value.read(1024))
        value.seek(0)  # Reset file pointer
        
        if file_type not in allowed_types:
            raise serializers.ValidationError(
                _('Bestandstype niet toegestaan. Toegestane types: JPG, PNG, GIF, PDF, DOC, DOCX, XLS, XLSX')
            )
        
        return value


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer voor het aanmaken van contactberichten (publieke API).
    
    TECHNISCHE CONCEPTEN:
    - CAPTCHA veld (kan later toegevoegd worden)
    - Auto-herkenning van categorie
    - IP en user agent tracking
    """
    
    attachments = ContactAttachmentSerializer(many=True, required=False, read_only=True)
    category_slug = serializers.CharField(
        write_only=True,
        required=True,
        help_text=_('Slug van de categorie')
    )
    
    # Voor CAPTCHA (optioneel)
    captcha_token = serializers.CharField(
        write_only=True,
        required=False,
        help_text=_('CAPTCHA token voor spam preventie')
    )
    
    class Meta:
        model = ContactMessage
        fields = [
            'full_name', 'email', 'phone_number', 'company_name',
            'category_slug', 'subject', 'message',
            'page_url', 'captcha_token', 'attachments'
        ]
    
    def validate_category_slug(self, value):
        """Valideer dat categorie bestaat en actief is"""
        try:
            category = ContactCategory.objects.get(slug=value, is_active=True)
        except ContactCategory.DoesNotExist:
            raise serializers.ValidationError(
                _('Categorie niet gevonden of niet actief')
            )
        return category
    
    def validate(self, attrs):
        """Globale validatie"""
        # Verwijder captcha_token uit attrs (wordt niet in model opgeslagen)
        attrs.pop('captcha_token', None)
        
        # Valideer e-mail frequentie (spam preventie)
        email = attrs.get('email')
        if email:
            recent_count = ContactMessage.objects.filter(
                email=email,
                created_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).count()
            
            if recent_count >= 5:
                raise serializers.ValidationError(
                    _('Te veel berichten verzonden in korte tijd. Probeer het later opnieuw.')
                )
        
        # Valideer bericht inhoud
        message = attrs.get('message', '').strip()
        if len(message) < 10:
            raise serializers.ValidationError(
                _('Bericht moet minimaal 10 karakters bevatten')
            )
        
        if len(message) > 5000:
            raise serializers.ValidationError(
                _('Bericht mag niet langer zijn dan 5000 karakters')
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create contact message met extra metadata"""
        request = self.context.get('request')
        
        # Haal categorie uit validated_data
        category = validated_data.pop('category_slug')
        
        # IP adres en user agent
        if request:
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            validated_data['ip_address'] = ip_address
            validated_data['user_agent'] = user_agent
        
        # Maak bericht aan
        message = ContactMessage.objects.create(
            category=category,
            **validated_data
        )
        
        return message
    
    def _get_client_ip(self, request):
        """Haal client IP adres op"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ContactMessageDetailSerializer(serializers.ModelSerializer):
    """
    Serializer voor gedetailleerde weergave van contactberichten.
    
    TECHNISCHE CONCEPTEN:
    - Nested categorie informatie
    - Bijlagen in base64 of URL vorm
    - Response tijd berekening
    """
    
    category = ContactCategorySerializer(read_only=True)
    attachments = ContactAttachmentSerializer(many=True, read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    response_time_display = serializers.SerializerMethodField()
    is_high_priority = serializers.BooleanField(read_only=True)
    is_urgent = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = [
            'uuid', 'reference_number', 'full_name', 'email', 'phone_number',
            'company_name', 'category', 'subject', 'message', 'status',
            'priority', 'ip_address', 'page_url', 'assigned_to',
            'assigned_to_email', 'assigned_to_name', 'response_notes',
            'responded_at', 'related_product', 'related_service',
            'related_quote', 'attachments', 'response_time_display',
            'is_high_priority', 'is_urgent', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'uuid', 'reference_number', 'ip_address', 'created_at',
            'updated_at'
        ]
    
    def get_response_time_display(self, obj):
        """Formatteer response tijd voor display"""
        if obj.response_time:
            total_seconds = obj.response_time.total_seconds()
            
            if total_seconds < 60:
                return f"{int(total_seconds)} seconden"
            elif total_seconds < 3600:
                return f"{int(total_seconds / 60)} minuten"
            elif total_seconds < 86400:
                return f"{int(total_seconds / 3600)} uur"
            else:
                return f"{int(total_seconds / 86400)} dagen"
        return None


class ContactMessageUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer voor het updaten van contactberichten (admin).
    
    TECHNISCHE CONCEPTEN:
    - Status transitie validatie
    - Notitie logging
    - Toewijzing validatie
    """
    
    class Meta:
        model = ContactMessage
        fields = [
            'status', 'priority', 'assigned_to', 'response_notes'
        ]
    
    def validate(self, attrs):
        """Valideer status transities"""
        instance = self.instance
        user = self.context.get('request').user
        
        # Controleer of gebruiker bevoegd is voor toewijzing
        if 'assigned_to' in attrs and attrs['assigned_to']:
            if not user.is_staff:
                raise serializers.ValidationError(
                    _('Alleen staff leden kunnen berichten toewijzen')
                )
        
        # Status transitie logica
        new_status = attrs.get('status')
        if new_status and instance:
            valid_transitions = {
                'new': ['read', 'in_progress', 'spam'],
                'read': ['in_progress', 'spam'],
                'in_progress': ['awaiting_reply', 'resolved', 'closed'],
                'awaiting_reply': ['in_progress', 'resolved'],
                'resolved': ['closed'],
                'closed': [],  # Geen transitie mogelijk
                'spam': [],  # Geen transitie mogelijk
            }
            
            if instance.status in valid_transitions:
                if new_status not in valid_transitions[instance.status]:
                    raise serializers.ValidationError(
                        _('Ongeldige status transitie van {} naar {}').format(
                            instance.get_status_display(),
                            dict(ContactMessage.STATUS_CHOICES).get(new_status)
                        )
                    )
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update instance met notitie logging"""
        user = self.context.get('request').user
        
        # Log wijzigingen
        changes = []
        for field, new_value in validated_data.items():
            old_value = getattr(instance, field)
            if old_value != new_value:
                if field == 'assigned_to':
                    old_name = old_value.get_full_name() if old_value else 'Niemand'
                    new_name = new_value.get_full_name() if new_value else 'Niemand'
                    changes.append(f"Toegewezen aan gewijzigd van {old_name} naar {new_name}")
                elif field == 'status':
                    old_status = dict(ContactMessage.STATUS_CHOICES).get(old_value, old_value)
                    new_status = dict(ContactMessage.STATUS_CHOICES).get(new_value, new_value)
                    changes.append(f"Status gewijzigd van {old_status} naar {new_status}")
                elif field == 'priority':
                    changes.append(f"Prioriteit gewijzigd van {old_value} naar {new_value}")
        
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update responded_at als status 'resolved' of 'closed' wordt
        if 'status' in validated_data and validated_data['status'] in ['resolved', 'closed']:
            instance.responded_at = timezone.now()
        
        instance.save()
        
        # Voeg notitie toe over wijzigingen
        if changes and user:
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
            note = f"[{timestamp} door {user.email}]: " + "; ".join(changes)
            instance.add_response_note(note)
        
        return instance


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    """
    Serializer voor nieuwsbrief inschrijvingen.
    
    TECHNISCHE CONCEPTEN:
    - Double opt-in flow
    - GDPR compliance
    - Subscription management
    """
    
    class Meta:
        model = NewsletterSubscriber
        fields = [
            'email', 'full_name', 'subscription_preferences',
            'is_confirmed', 'confirmed_at', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'is_confirmed', 'confirmed_at', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def validate_email(self, value):
        """Valideer e-mail en voorkom spam"""
        value = value.lower().strip()
        
        # Controleer of e-mail al bestaat
        if NewsletterSubscriber.objects.filter(email=value).exists():
            subscriber = NewsletterSubscriber.objects.get(email=value)
            if subscriber.is_active:
                raise serializers.ValidationError(
                    _('Dit e-mailadres is al ingeschreven voor de nieuwsbrief')
                )
            else:
                # Re-activate optie
                pass
        
        # E-mail domein validatie
        invalid_domains = ['tempmail.com', 'throwaway.com']  # Vul aan
        domain = value.split('@')[-1]
        if domain in invalid_domains:
            raise serializers.ValidationError(
                _('Tijdelijke e-mailadressen worden niet geaccepteerd')
            )
        
        return value
    
    def create(self, validated_data):
        """Create subscription met tokens"""
        request = self.context.get('request')
        
        # IP adres tracking
        if request:
            ip_address = self._get_client_ip(request)
            validated_data['ip_address'] = ip_address
        
        # Maak subscription
        subscriber = NewsletterSubscriber.objects.create(**validated_data)
        
        # TODO: Stuur bevestigingsmail
        # self._send_confirmation_email(subscriber)
        
        return subscriber
    
    def _get_client_ip(self, request):
        """Haal client IP adres op"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip