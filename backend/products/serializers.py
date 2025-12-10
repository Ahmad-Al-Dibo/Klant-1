from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import (
    ProductCategory, Product, ProductImage, 
    ProductFeature, ProductReview, ProductView
)


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer voor product categorieën"""
    product_count = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'description', 'image', 
            'parent', 'is_active', 'display_order',
            'product_count', 'subcategories',
            'meta_title', 'meta_description', 'meta_keywords',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_product_count(self, obj):
        """Aantal producten in categorie"""
        return obj.products.count()
    
    def get_subcategories(self, obj):
        """Subcategorieën recursief ophalen"""
        subcategories = obj.subcategories.all()
        if subcategories:
            return ProductCategorySerializer(subcategories, many=True).data
        return []


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer voor product afbeeldingen"""
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'image_url', 'thumbnail_url',
            'alt_text', 'caption', 'display_order', 'is_primary',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_image_url(self, obj):
        """Volledige image URL"""
        if obj.image:
            return obj.image.url
        return None
    
    def get_thumbnail_url(self, obj):
        """Thumbnail URL (kan later geïmplementeerd worden met sorl-thumbnail)"""
        if obj.image:
            return obj.image.url  # Voor nu, zelfde als origineel
        return None


class ProductFeatureSerializer(serializers.ModelSerializer):
    """Serializer voor product kenmerken"""
    
    class Meta:
        model = ProductFeature
        fields = ['id', 'name', 'value', 'icon', 'display_order']


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer voor product beoordelingen"""
    reviewer_name_display = serializers.SerializerMethodField()
    rating_display = serializers.SerializerMethodField()
    helpful_score = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'user', 'rating', 'rating_display',
            'title', 'comment', 'reviewer_name', 'reviewer_email',
            'reviewer_name_display', 'is_approved', 'is_verified_purchase',
            'helpful_yes', 'helpful_no', 'helpful_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'user': {'read_only': True},
            'reviewer_email': {'write_only': True},
        }
    
    def get_reviewer_name_display(self, obj):
        """Toon reviewer naam (anoniem als niet goedgekeurd)"""
        if obj.is_approved:
            if obj.user:
                return obj.user.get_full_name() or obj.user.email
            return obj.reviewer_name or _('Anonieme klant')
        return _('Beoordeling in afwachting')
    
    def get_rating_display(self, obj):
        """Sterren rating display"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return stars
    
    def get_helpful_score(self, obj):
        return obj.helpful_score
    
    def create(self, validated_data):
        """Auto-vul user indien ingelogd"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            if not validated_data.get('reviewer_name'):
                validated_data['reviewer_name'] = request.user.get_full_name() or request.user.email
        
        # Voor niet-ingelogde gebruikers, standaard niet goedgekeurd
        if not validated_data.get('user'):
            validated_data['is_approved'] = False
        
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer voor product lijsten (light versie)"""
    categories = ProductCategorySerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'short_description',
            'categories', 'primary_image',
            'price', 'original_price', 'sale_price', 'is_on_sale',
            'final_price', 'discount_percentage',
            'condition', 'status', 'brand', 'model',
            'is_featured', 'is_bestseller', 'views_count',
            'avg_rating', 'review_count',
            'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Haal primaire afbeelding op"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        
        # Fallback naar eerste afbeelding
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None
    
    def get_discount_percentage(self, obj):
        return obj.discount_percentage
    
    def get_avg_rating(self, obj):
        """Bereken gemiddelde rating"""
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            return round(total / reviews.count(), 1)
        return 0
    
    def get_review_count(self, obj):
        """Tel aantal goedgekeurde reviews"""
        return obj.reviews.filter(is_approved=True).count()


class ProductDetailSerializer(ProductListSerializer):
    """Serializer voor product detail pagina"""
    images = ProductImageSerializer(many=True, read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    is_low_stock = serializers.BooleanField(read_only=True)
    requires_assembly = serializers.BooleanField(read_only=True)
    assembly_service_available = serializers.BooleanField(read_only=True)
    delivery_available = serializers.BooleanField(read_only=True)
    
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            'full_description', 'images', 'features',
            'dimensions', 'weight', 'material', 'color',
            'stock_quantity', 'low_stock_threshold', 'is_low_stock',
            'sku', 'requires_assembly', 'assembly_service_available',
            'delivery_available', 'meta_title', 'meta_description', 'meta_keywords',
            'published_at', 'reviews'
        ]
    
    def get_reviews(self, obj):
        """Haal alleen goedgekeurde reviews op"""
        approved_reviews = obj.reviews.filter(is_approved=True).order_by('-created_at')[:10]
        return ProductReviewSerializer(approved_reviews, many=True).data


class ProductViewSerializer(serializers.ModelSerializer):
    """Serializer voor product view logging"""
    
    class Meta:
        model = ProductView
        fields = ['id', 'product', 'user', 'session_key', 
                 'ip_address', 'user_agent', 'referrer', 'created_at']
        read_only_fields = ['created_at']


class ProductSearchSerializer(serializers.Serializer):
    """Serializer voor product zoekopdrachten"""
    q = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    condition = serializers.CharField(required=False, allow_blank=True)
    brand = serializers.CharField(required=False, allow_blank=True)
    material = serializers.CharField(required=False, allow_blank=True)
    color = serializers.CharField(required=False, allow_blank=True)
    requires_assembly = serializers.BooleanField(required=False)
    delivery_available = serializers.BooleanField(required=False)
    sort_by = serializers.ChoiceField(choices=[
        ('newest', 'Nieuwste eerst'),
        ('price_low', 'Prijs: laag naar hoog'),
        ('price_high', 'Prijs: hoog naar laag'),
        ('popular', 'Populair'),
        ('rating', 'Hoogste beoordeling'),
    ], required=False, default='newest')
    page = serializers.IntegerField(min_value=1, required=False, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, required=False, default=20)
    
    def validate(self, data):
        """Valideer zoekparameters"""
        if data.get('min_price') and data.get('max_price'):
            if data['min_price'] > data['max_price']:
                raise serializers.ValidationError({
                    'min_price': 'Minimum prijs kan niet hoger zijn dan maximum prijs'
                })
        return data