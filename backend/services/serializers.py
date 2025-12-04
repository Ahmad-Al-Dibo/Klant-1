from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import (
    ServiceCategory, Service, ServiceImage, FAQ,
    ServiceFeature, ServicePackage, ServiceArea,
    Testimonial, ServiceView
)


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer voor dienst categorieën"""
    service_count = serializers.SerializerMethodField()
    icon_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceCategory
        fields = [
            'id', 'name', 'slug', 'category_type', 'icon', 'icon_display',
            'description', 'image', 'display_order', 'is_active',
            'show_on_homepage', 'service_count',
            'meta_title', 'meta_description', 'meta_keywords',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_service_count(self, obj):
        return obj.services.filter(is_active=True).count()
    
    def get_icon_display(self, obj):
        return obj.icon if obj.icon else 'fas fa-cog'


class ServiceImageSerializer(serializers.ModelSerializer):
    """Serializer voor dienst afbeeldingen"""
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceImage
        fields = [
            'id', 'image', 'image_url', 'thumbnail_url',
            'caption', 'alt_text', 'is_before_image', 'is_after_image',
            'display_order', 'is_primary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def get_thumbnail_url(self, obj):
        if obj.image:
            return obj.image.url  # Voor nu zelfde als origineel
        return None


class FAQSerializer(serializers.ModelSerializer):
    """Serializer voor veelgestelde vragen"""
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'display_order', 
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ServiceFeatureSerializer(serializers.ModelSerializer):
    """Serializer voor dienst kenmerken"""
    
    class Meta:
        model = ServiceFeature
        fields = ['id', 'title', 'description', 'icon', 'display_order']


class ServicePackageSerializer(serializers.ModelSerializer):
    """Serializer voor dienst pakketten"""
    
    class Meta:
        model = ServicePackage
        fields = [
            'id', 'name', 'description', 'price', 'duration',
            'includes', 'excludes', 'is_popular', 'display_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ServiceAreaSerializer(serializers.ModelSerializer):
    """Serializer voor dienst gebieden"""
    
    class Meta:
        model = ServiceArea
        fields = ['id', 'city', 'postal_code', 'region', 'is_active']


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer voor testimonials"""
    rating_stars = serializers.SerializerMethodField()
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'service', 'service_name', 'client_name', 
            'client_location', 'client_company', 'content',
            'rating', 'rating_stars', 'is_approved', 'is_featured',
            'display_order', 'project_date', 'project_description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'is_approved': {'read_only': True},
            'is_featured': {'read_only': True},
        }
    
    def get_rating_stars(self, obj):
        return obj.rating_stars
    
    def create(self, validated_data):
        """Auto goedkeuring voor admin users"""
        request = self.context.get('request')
        if request and request.user.is_staff:
            validated_data['is_approved'] = True
        return super().create(validated_data)


class ServiceListSerializer(serializers.ModelSerializer):
    """Serializer voor dienst lijsten (light versie)"""
    category = ServiceCategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    faq_count = serializers.SerializerMethodField()
    testimonial_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'slug', 'category', 'short_description',
            'primary_image', 'has_fixed_price', 'fixed_price',
            'price_description', 'estimated_time', 'is_popular',
            'is_featured', 'is_active', 'requires_quote',
            'can_book_online', 'has_emergency_service',
            'views_count', 'quote_requests_count',
            'faq_count', 'testimonial_count',
            'created_at', 'updated_at'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ServiceImageSerializer(primary_image).data
        
        first_image = obj.images.first()
        if first_image:
            return ServiceImageSerializer(first_image).data
        return None
    
    def get_faq_count(self, obj):
        return obj.faqs.filter(is_active=True).count()
    
    def get_testimonial_count(self, obj):
        return obj.testimonials.filter(is_approved=True).count()


class ServiceDetailSerializer(ServiceListSerializer):
    """Serializer voor dienst detail pagina"""
    images = ServiceImageSerializer(many=True, read_only=True)
    faqs = FAQSerializer(many=True, read_only=True)
    features = ServiceFeatureSerializer(many=True, read_only=True)
    packages = ServicePackageSerializer(many=True, read_only=True)
    areas = ServiceAreaSerializer(many=True, read_only=True)
    testimonials = serializers.SerializerMethodField()
    
    class Meta(ServiceListSerializer.Meta):
        fields = ServiceListSerializer.Meta.fields + [
            'full_description', 'benefits', 'process',
            'requirements', 'images', 'faqs', 'features',
            'packages', 'areas', 'testimonials',
            'meta_title', 'meta_description', 'meta_keywords',
            'published_at'
        ]
    
    def get_testimonials(self, obj):
        """Haal alleen goedgekeurde testimonials op"""
        testimonials = obj.testimonials.filter(
            is_approved=True
        ).order_by('-is_featured', 'display_order', '-created_at')[:10]
        return TestimonialSerializer(testimonials, many=True).data


class ServiceViewSerializer(serializers.ModelSerializer):
    """Serializer voor service view logging"""
    
    class Meta:
        model = ServiceView
        fields = ['id', 'service', 'user', 'session_key', 
                 'ip_address', 'user_agent', 'referrer', 'created_at']
        read_only_fields = ['created_at']


class ServiceSearchSerializer(serializers.Serializer):
    """Serializer voor dienst zoekopdrachten"""
    q = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    has_fixed_price = serializers.BooleanField(required=False)
    can_book_online = serializers.BooleanField(required=False)
    has_emergency_service = serializers.BooleanField(required=False)
    city = serializers.CharField(required=False, allow_blank=True)
    sort_by = serializers.ChoiceField(choices=[
        ('newest', 'Nieuwste eerst'),
        ('popular', 'Populairste'),
        ('name', 'Naam A-Z'),
        ('price_low', 'Prijs: laag naar hoog'),
        ('price_high', 'Prijs: hoog naar laag'),
    ], required=False, default='newest')
    page = serializers.IntegerField(min_value=1, required=False, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, required=False, default=20)