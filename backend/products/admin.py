from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ProductCategory, Product, ProductImage,
    ProductFeature, ProductReview, ProductView
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'caption', 'display_order', 'is_primary']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Voorbeeld'


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1
    fields = ['name', 'value', 'icon', 'display_order']


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    fields = ['user', 'rating', 'title', 'is_approved', 'created_at']
    readonly_fields = ['created_at']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active', 'display_order', 'product_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basis informatie', {
            'fields': ('name', 'slug', 'description', 'image', 'parent')
        }),
        ('Weergave', {
            'fields': ('is_active', 'display_order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Aantal producten'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'sku', 'brand', 'condition', 'status', 
                   'price', 'stock_quantity', 'is_featured', 'created_at']
    list_filter = ['status', 'condition', 'is_featured', 'is_bestseller', 
                  'requires_assembly', 'delivery_available', 'categories']
    search_fields = ['title', 'sku', 'brand', 'model']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    inlines = [ProductImageInline, ProductFeatureInline, ProductReviewInline]
    fieldsets = (
        ('Basis informatie', {
            'fields': ('title', 'slug', 'short_description', 'full_description', 'categories')
        }),
        ('Prijzen', {
            'fields': ('price', 'original_price', 'is_on_sale', 'sale_price')
        }),
        ('Voorraad & Conditie', {
            'fields': ('sku', 'stock_quantity', 'low_stock_threshold', 
                      'condition', 'status')
        }),
        ('Specificaties', {
            'fields': ('brand', 'model', 'dimensions', 'weight', 
                      'material', 'color')
        }),
        ('Diensten', {
            'fields': ('requires_assembly', 'assembly_service_available', 
                      'delivery_available')
        }),
        ('Promotie', {
            'fields': ('is_featured', 'is_bestseller', 'views_count')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'reviewer_name', 'rating', 'is_approved', 
                   'is_verified_purchase', 'created_at']
    list_filter = ['is_approved', 'rating', 'is_verified_purchase']
    search_fields = ['product__title', 'reviewer_name', 'comment']
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Selectie goedkeuren"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = "Selectie afkeuren"


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__title', 'user__email', 'ip_address']
    readonly_fields = ['product', 'user', 'session_key', 'ip_address', 
                      'user_agent', 'referrer', 'created_at']
    
    def has_add_permission(self, request):
        return False