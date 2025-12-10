from django.db.models import Q, Count, Avg, Sum
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from clients import models

from .models import (
    ProductCategory, Product, ProductImage, 
    ProductFeature, ProductReview, ProductView
)
from .serializers import (
    ProductCategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ProductReviewSerializer,
    ProductSearchSerializer, ProductViewSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .filters import ProductFilter
import logging

logger = logging.getLogger(__name__)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor product categorieën
    """
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filter op parent voor hiërarchische weergave"""
        queryset = super().get_queryset()
        
        # Filter op parent voor subcategorieën
        parent_slug = self.request.query_params.get('parent', None)
        if parent_slug:
            queryset = queryset.filter(parent__slug=parent_slug)
        
        # Alleen root categorieën
        only_root = self.request.query_params.get('root_only', None)
        if only_root:
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Haal producten in categorie op"""
        category = self.get_object()
        
        # Haal alle producten in categorie en subcategorieën
        all_categories = category.get_descendants(include_self=True)
        products = Product.objects.filter(
            categories__in=all_categories,
            status='available'
        ).distinct()
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor producten
    """
    queryset = Product.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'short_description', 'full_description', 'brand', 'model']
    ordering_fields = ['price', 'created_at', 'views_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Gebruik verschillende serializers voor list en detail"""
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        """Pas queryset aan op basis van actie en filters"""
        queryset = super().get_queryset()
        
        # Voor niet-admin gebruikers, toon alleen beschikbare producten
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='available')
        
        # Filter op featured
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Filter op bestsellers
        bestseller = self.request.query_params.get('bestseller', None)
        if bestseller == 'true':
            queryset = queryset.filter(is_bestseller=True)
        
        # Filter op sale
        on_sale = self.request.query_params.get('on_sale', None)
        if on_sale == 'true':
            queryset = queryset.filter(is_on_sale=True)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Log product view bij het ophalen"""
        instance = self.get_object()
        
        # Increment view count
        instance.increment_views()
        
        # Log de view voor analytics
        self._log_product_view(instance, request)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def _log_product_view(self, product, request):
        """Log een productweergave"""
        try:
            ProductView.objects.create(
                product=product,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key or '',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER', '')
            )
        except Exception as e:
            logger.error(f"Error logging product view: {e}")
    
    def _get_client_ip(self, request):
        """Haal client IP adres op"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, slug=None):
        """Manueel increment view count (voor frontend tracking)"""
        product = self.get_object()
        product.increment_views()
        return Response({'status': 'view count incremented'})
    
    @action(detail=True, methods=['get'])
    def similar(self, request, slug=None):
        """Vind vergelijkbare producten"""
        product = self.get_object()
        
        # Zoek vergelijkbare producten op basis van categorieën
        similar_products = Product.objects.filter(
            categories__in=product.categories.all(),
            status='available'
        ).exclude(
            id=product.id
        ).distinct()[:8]
        
        serializer = ProductListSerializer(similar_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Haal uitgelichte producten op"""
        featured_products = self.get_queryset().filter(
            is_featured=True,
            status='available'
        )[:12]
        
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def bestsellers(self, request):
        """Haal bestsellers op"""
        # Hier kan je een echte bestseller logica implementeren
        bestsellers = self.get_queryset().filter(
            is_bestseller=True,
            status='available'
        )[:12]
        
        serializer = self.get_serializer(bestsellers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Haal producten in de aanbieding op"""
        sale_products = self.get_queryset().filter(
            is_on_sale=True,
            status='available'
        )[:12]
        
        serializer = self.get_serializer(sale_products, many=True)
        return Response(serializer.data)


class ProductSearchView(generics.ListAPIView):
    """
    Geavanceerde product zoekfunctionaliteit
    """
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Product.objects.filter(status='available')
        search_params = ProductSearchSerializer(data=self.request.query_params)
        
        if search_params.is_valid():
            data = search_params.validated_data
            
            # Zoek op tekst
            if data.get('q'):
                queryset = queryset.filter(
                    Q(title__icontains=data['q']) |
                    Q(short_description__icontains=data['q']) |
                    Q(full_description__icontains=data['q']) |
                    Q(brand__icontains=data['q']) |
                    Q(model__icontains=data['q'])
                )
            
            # Filter op categorie
            if data.get('category'):
                queryset = queryset.filter(categories__slug=data['category'])
            
            # Filter op prijs
            if data.get('min_price'):
                queryset = queryset.filter(price__gte=data['min_price'])
            if data.get('max_price'):
                queryset = queryset.filter(price__lte=data['max_price'])
            
            # Andere filters
            if data.get('condition'):
                queryset = queryset.filter(condition=data['condition'])
            if data.get('brand'):
                queryset = queryset.filter(brand__iexact=data['brand'])
            if data.get('material'):
                queryset = queryset.filter(material__icontains=data['material'])
            if data.get('color'):
                queryset = queryset.filter(color__icontains=data['color'])
            if data.get('requires_assembly') is not None:
                queryset = queryset.filter(requires_assembly=data['requires_assembly'])
            if data.get('delivery_available') is not None:
                queryset = queryset.filter(delivery_available=data['delivery_available'])
            
            # Sortering
            if data.get('sort_by') == 'price_low':
                queryset = queryset.order_by('price')
            elif data.get('sort_by') == 'price_high':
                queryset = queryset.order_by('-price')
            elif data.get('sort_by') == 'popular':
                queryset = queryset.order_by('-views_count')
            elif data.get('sort_by') == 'rating':
                # Sorteer op gemiddelde rating
                queryset = queryset.annotate(
                    avg_rating=Avg('reviews__rating')
                ).order_by('-avg_rating')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Voeg zoekmetadata toe aan response"""
        response = super().list(request, *args, **kwargs)
        
        # Tel resultaten
        count = self.get_queryset().count()
        
        # Voeg metadata toe
        response.data = {
            'count': count,
            'results': response.data,
            'search_params': request.query_params.dict()
        }
        
        return response


class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor product beoordelingen
    """
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """Filter reviews op product"""
        queryset = super().get_queryset()
        
        # Voor niet-admin gebruikers, toon alleen goedgekeurde reviews
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        # Filter op product
        product_slug = self.request.query_params.get('product', None)
        if product_slug:
            queryset = queryset.filter(product__slug=product_slug)
        
        return queryset
    
    def perform_create(self, serializer):
        """Sla de review op"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Markeer review als handig"""
        review = self.get_object()
        helpful_type = request.data.get('type', 'yes')
        
        if helpful_type == 'yes':
            review.helpful_yes += 1
        else:
            review.helpful_no += 1
        
        review.save()
        return Response({'status': 'helpful vote recorded'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        """Rapporteer een review"""
        review = self.get_object()
        reason = request.data.get('reason', '')
        
        # Hier kan je de rapportage logica implementeren
        # Bijvoorbeeld: email naar admin, vlag in database, etc.
        
        logger.info(f"Review {pk} reported by user {request.user}: {reason}")
        return Response({'status': 'review reported'})


class ProductStatisticsView(generics.GenericAPIView):
    """
    Statistieken voor producten
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Haal product statistieken op"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Totale statistieken
        total_products = Product.objects.count()
        available_products = Product.objects.filter(status='available').count()
        sold_products = Product.objects.filter(status='sold').count()
        
        # Voorraad statistieken
        low_stock_products = Product.objects.filter(
            status='available',
            stock_quantity__lte=models.F('low_stock_threshold')
        ).count()
        
        # Categorie statistieken
        category_stats = ProductCategory.objects.annotate(
            product_count=Count('products')
        ).values('name', 'product_count')
        
        # Verkoop statistieken (vereenvoudigd)
        total_revenue = Product.objects.aggregate(
            total=Sum('price')
        )['total'] or 0
        
        data = {
            'total_products': total_products,
            'available_products': available_products,
            'sold_products': sold_products,
            'low_stock_products': low_stock_products,
            'category_stats': list(category_stats),
            'total_revenue': float(total_revenue),
        }
        
        return Response(data)