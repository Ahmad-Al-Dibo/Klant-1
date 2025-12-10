import django_filters
from django.db.models import Q
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """Filters voor producten"""
    
    # Text search filter
    search = django_filters.CharFilter(method='filter_search')
    
    # Price range filters
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Category filter (can accept multiple categories)
    category = django_filters.CharFilter(method='filter_category')
    
    # Condition filter
    condition = django_filters.CharFilter(field_name='condition')
    
    # Brand filter
    brand = django_filters.CharFilter(field_name='brand', lookup_expr='iexact')
    
    # Material filter
    material = django_filters.CharFilter(field_name='material', lookup_expr='icontains')
    
    # Color filter
    color = django_filters.CharFilter(field_name='color', lookup_expr='icontains')
    
    # Boolean filters
    requires_assembly = django_filters.BooleanFilter(field_name='requires_assembly')
    delivery_available = django_filters.BooleanFilter(field_name='delivery_available')
    assembly_service_available = django_filters.BooleanFilter(field_name='assembly_service_available')
    
    # Status filter (for admin only)
    status = django_filters.CharFilter(field_name='status')
    
    class Meta:
        model = Product
        fields = [
            'search', 'min_price', 'max_price', 'category',
            'condition', 'brand', 'material', 'color',
            'requires_assembly', 'delivery_available', 'assembly_service_available',
            'status'
        ]
    
    def filter_search(self, queryset, name, value):
        """Search in multiple fields"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(short_description__icontains=value) |
            Q(full_description__icontains=value) |
            Q(brand__icontains=value) |
            Q(model__icontains=value)
        )
    
    def filter_category(self, queryset, name, value):
        """Filter by category slug"""
        return queryset.filter(categories__slug=value)