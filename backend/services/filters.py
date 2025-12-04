import django_filters
from django.db.models import Q
from .models import Service


class ServiceFilter(django_filters.FilterSet):
    """Filters voor diensten"""
    
    # Text search filter
    search = django_filters.CharFilter(method='filter_search')
    
    # Category filter
    category = django_filters.CharFilter(field_name='category__slug')
    
    # Boolean filters
    has_fixed_price = django_filters.BooleanFilter(field_name='has_fixed_price')
    can_book_online = django_filters.BooleanFilter(field_name='can_book_online')
    has_emergency_service = django_filters.BooleanFilter(field_name='has_emergency_service')
    
    # Price filter (voor vaste prijzen)
    min_price = django_filters.NumberFilter(field_name='fixed_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='fixed_price', lookup_expr='lte')
    
    # City filter
    city = django_filters.CharFilter(method='filter_city')
    
    # Status filter (voor admin only)
    is_active = django_filters.BooleanFilter(field_name='is_active')
    
    class Meta:
        model = Service
        fields = [
            'search', 'category', 'has_fixed_price', 'can_book_online',
            'has_emergency_service', 'min_price', 'max_price', 'city',
            'is_active'
        ]
    
    def filter_search(self, queryset, name, value):
        """Search in multiple fields"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(short_description__icontains=value) |
            Q(full_description__icontains=value) |
            Q(benefits__icontains=value) |
            Q(process__icontains=value)
        )
    
    def filter_city(self, queryset, name, value):
        """Filter by city in service areas"""
        return queryset.filter(areas__city__iexact=value)