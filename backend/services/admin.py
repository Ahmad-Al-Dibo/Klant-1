from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ServiceCategory, Service, ServiceImage, FAQ,
    ServiceFeature, ServicePackage, ServiceArea,
    Testimonial, ServiceView
)


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ['image', 'caption', 'alt_text', 'is_before_image', 
             'is_after_image', 'display_order', 'is_primary']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Voorbeeld'


class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1
    fields = ['question', 'answer', 'display_order', 'is_active']


class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1
    fields = ['title', 'description', 'icon', 'display_order']


class ServicePackageInline(admin.TabularInline):
    model = ServicePackage
    extra = 1
    fields = ['name', 'description', 'price', 'duration', 
             'includes', 'excludes', 'is_popular', 'display_order']


class ServiceAreaInline(admin.TabularInline):
    model = ServiceArea
    extra = 1
    fields = ['city', 'postal_code', 'region', 'is_active']


class TestimonialInline(admin.TabularInline):
    model = Testimonial
    extra = 0
    fields = ['client_name', 'rating', 'content', 'is_approved', 'is_featured']
    readonly_fields = ['created_at']


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'icon', 'display_order', 
                   'is_active', 'show_on_homepage', 'service_count']
    list_filter = ['is_active', 'show_on_homepage', 'category_type']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basis informatie', {
            'fields': ('name', 'slug', 'category_type', 'icon', 'description', 'image')
        }),
        ('Weergave', {
            'fields': ('display_order', 'is_active', 'show_on_homepage')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    def service_count(self, obj):
        return obj.services.count()
    service_count.short_description = 'Aantal diensten'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'has_fixed_price', 'fixed_price',
                   'is_popular', 'is_featured', 'is_active', 'views_count']
    list_filter = ['is_active', 'is_popular', 'is_featured', 'category',
                  'has_fixed_price', 'can_book_online', 'has_emergency_service']
    search_fields = ['name', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views_count', 'quote_requests_count', 
                      'created_at', 'updated_at']
    inlines = [ServiceImageInline, FAQInline, ServiceFeatureInline,
              ServicePackageInline, ServiceAreaInline, TestimonialInline]
    fieldsets = (
        ('Basis informatie', {
            'fields': ('name', 'slug', 'category', 'short_description', 'full_description')
        }),
        ('Details', {
            'fields': ('benefits', 'process', 'requirements')
        }),
        ('Prijzen & Tijden', {
            'fields': ('has_fixed_price', 'fixed_price', 'price_description', 'estimated_time')
        }),
        ('Kenmerken', {
            'fields': ('is_popular', 'is_featured', 'is_active')
        }),
        ('Functionaliteit', {
            'fields': ('requires_quote', 'can_book_online', 'has_emergency_service')
        }),
        ('Statistieken', {
            'fields': ('views_count', 'quote_requests_count'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Publicatie', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'service', 'rating', 'is_approved', 
                   'is_featured', 'created_at']
    list_filter = ['is_approved', 'is_featured', 'rating', 'service']
    search_fields = ['client_name', 'content', 'service__name']
    actions = ['approve_testimonials', 'feature_testimonials']
    
    def approve_testimonials(self, request, queryset):
        queryset.update(is_approved=True)
    approve_testimonials.short_description = "Selectie goedkeuren"
    
    def feature_testimonials(self, request, queryset):
        queryset.update(is_featured=True)
    feature_testimonials.short_description = "Selectie uitlichten"


@admin.register(ServiceView)
class ServiceViewAdmin(admin.ModelAdmin):
    list_display = ['service', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['service__name', 'user__email', 'ip_address']
    readonly_fields = ['service', 'user', 'session_key', 'ip_address', 
                      'user_agent', 'referrer', 'created_at']
    
    def has_add_permission(self, request):
        return False