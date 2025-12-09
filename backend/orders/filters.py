import django_filters
from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import Order, OrderItem, Payment


class OrderFilter(filters.FilterSet):
    """
    Filter voor orders.
    
    TECHNISCHE CONCEPTEN:
    - Date range filtering
    - Multiple choice filtering
    - Related model filtering
    - Price range filtering
    """
    
    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='exact'
    )
    
    priority = django_filters.CharFilter(
        field_name='priority',
        lookup_expr='exact'
    )
    
    payment_status = django_filters.CharFilter(
        field_name='payment_status',
        lookup_expr='exact'
    )
    
    client = django_filters.CharFilter(
        field_name='client__company_name',
        lookup_expr='icontains'
    )
    
    client_id = django_filters.UUIDFilter(
        field_name='client__id',
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
    
    delivery_after = django_filters.DateTimeFilter(
        field_name='delivery_date',
        lookup_expr='gte'
    )
    
    delivery_before = django_filters.DateTimeFilter(
        field_name='delivery_date',
        lookup_expr='lte'
    )
    
    payment_due_after = django_filters.DateFilter(
        field_name='payment_due_date',
        lookup_expr='gte'
    )
    
    payment_due_before = django_filters.DateFilter(
        field_name='payment_due_date',
        lookup_expr='lte'
    )
    
    min_total = django_filters.NumberFilter(
        field_name='total_incl_tax',
        lookup_expr='gte'
    )
    
    max_total = django_filters.NumberFilter(
        field_name='total_incl_tax',
        lookup_expr='lte'
    )
    
    has_quote = django_filters.BooleanFilter(
        field_name='quote',
        lookup_expr='isnull',
        exclude=True
    )
    
    tags = django_filters.CharFilter(
        method='filter_tags'
    )
    
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Order
        fields = [
            'status', 'priority', 'payment_status', 'client',
            'assigned_to', 'created_after', 'created_before',
            'delivery_after', 'delivery_before', 'payment_due_after',
            'payment_due_before', 'min_total', 'max_total',
            'has_quote', 'tags'
        ]
    
    def filter_tags(self, queryset, name, value):
        """Filter op tags"""
        tag_slugs = value.split(',')
        return queryset.filter(tags__slug__in=tag_slugs).distinct()
    
    def filter_search(self, queryset, name, value):
        """Geavanceerde zoekfunctionaliteit"""
        return queryset.filter(
            Q(order_number__icontains=value) |
            Q(reference__icontains=value) |
            Q(client__company_name__icontains=value) |
            Q(client__email__icontains=value) |
            Q(tracking_number__icontains=value) |
            Q(internal_notes__icontains=value) |
            Q(client_notes__icontains=value)
        )


class OrderItemFilter(filters.FilterSet):
    """
    Filter voor order items.
    """
    
    item_type = django_filters.CharFilter(
        field_name='item_type',
        lookup_expr='exact'
    )
    
    is_delivered = django_filters.BooleanFilter()
    
    order = django_filters.CharFilter(
        field_name='order__order_number',
        lookup_expr='exact'
    )
    
    product = django_filters.CharFilter(
        field_name='product__slug',
        lookup_expr='exact'
    )
    
    service = django_filters.CharFilter(
        field_name='service__slug',
        lookup_expr='exact'
    )
    
    class Meta:
        model = OrderItem
        fields = ['item_type', 'is_delivered', 'order', 'product', 'service']


class PaymentFilter(filters.FilterSet):
    """
    Filter voor betalingen.
    """
    
    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='exact'
    )
    
    payment_method = django_filters.CharFilter(
        field_name='payment_method',
        lookup_expr='exact'
    )
    
    order = django_filters.CharFilter(
        field_name='order__order_number',
        lookup_expr='exact'
    )
    
    payer_email = django_filters.CharFilter(
        field_name='payer_email',
        lookup_expr='icontains'
    )
    
    payment_after = django_filters.DateTimeFilter(
        field_name='payment_date',
        lookup_expr='gte'
    )
    
    payment_before = django_filters.DateTimeFilter(
        field_name='payment_date',
        lookup_expr='lte'
    )
    
    min_amount = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte'
    )
    
    max_amount = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte'
    )
    
    class Meta:
        model = Payment
        fields = [
            'status', 'payment_method', 'order', 'payer_email',
            'payment_after', 'payment_before', 'min_amount', 'max_amount'
        ]