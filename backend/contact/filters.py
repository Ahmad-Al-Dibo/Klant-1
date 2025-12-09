import django_filters
from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import ContactCategory, ContactMessage


class ContactCategoryFilter(filters.FilterSet):
    """
    Filter voor contactcategorieën.
    
    TECHNISCHE CONCEPTEN:
    - Multiple choice filtering
    - Boolean filtering
    - Range filtering
    """
    
    category_type = django_filters.CharFilter(
        field_name='category_type',
        lookup_expr='exact'
    )
    
    is_active = django_filters.BooleanFilter()
    
    parent = django_filters.CharFilter(
        field_name='parent__slug',
        lookup_expr='exact'
    )
    
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = ContactCategory
        fields = ['category_type', 'is_active', 'parent']
    
    def filter_search(self, queryset, name, value):
        """Zoek in naam en beschrijving"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class ContactMessageFilter(filters.FilterSet):
    """
    Geavanceerde filtering voor contactberichten.
    
    TECHNISCHE CONCEPTEN:
    - Date range filtering
    - Multiple choice filtering
    - Related model filtering
    - Priority range filtering
    """
    
    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='exact'
    )
    
    priority = django_filters.NumberFilter(
        field_name='priority',
        lookup_expr='exact'
    )
    
    priority_min = django_filters.NumberFilter(
        field_name='priority',
        lookup_expr='gte'
    )
    
    priority_max = django_filters.NumberFilter(
        field_name='priority',
        lookup_expr='lte'
    )
    
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )
    
    assigned_to = django_filters.NumberFilter(
        field_name='assigned_to__id',
        lookup_expr='exact'
    )
    
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    
    responded_after = django_filters.DateTimeFilter(
        field_name='responded_at',
        lookup_expr='gte'
    )
    
    responded_before = django_filters.DateTimeFilter(
        field_name='responded_at',
        lookup_expr='lte'
    )
    
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = ContactMessage
        fields = [
            'status', 'priority', 'category', 'assigned_to',
            'created_after', 'created_before',
            'responded_after', 'responded_before'
        ]
    
    def filter_search(self, queryset, name, value):
        """Geavanceerde zoekfunctionaliteit"""
        return queryset.filter(
            Q(full_name__icontains=value) |
            Q(email__icontains=value) |
            Q(company_name__icontains=value) |
            Q(subject__icontains=value) |
            Q(message__icontains=value) |
            Q(reference_number__icontains=value)
        )