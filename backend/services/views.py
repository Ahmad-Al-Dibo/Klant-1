from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .models import (
    ServiceCategory, Service, ServiceImage, FAQ,
    ServiceFeature, ServicePackage, ServiceArea,
    Testimonial, ServiceView
)
from .serializers import (
    ServiceCategorySerializer, ServiceListSerializer,
    ServiceDetailSerializer, TestimonialSerializer,
    ServiceSearchSerializer, ServiceViewSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .filters import ServiceFilter
import logging

logger = logging.getLogger(__name__)


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor dienst categorieën
    """
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Pas queryset aan op basis van filters"""
        queryset = super().get_queryset()
        
        # Filter op homepage weergave
        homepage = self.request.query_params.get('homepage', None)
        if homepage == 'true':
            queryset = queryset.filter(show_on_homepage=True)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def services(self, request, slug=None):
        """Haal diensten in categorie op"""
        category = self.get_object()
        services = category.services.filter(is_active=True)
        
        page = self.paginate_queryset(services)
        if page is not None:
            serializer = ServiceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ServiceListSerializer(services, many=True)
        return Response(serializer.data)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor diensten
    """
    queryset = Service.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['name', 'short_description', 'full_description', 'benefits']
    ordering_fields = ['name', 'views_count', 'quote_requests_count']
    ordering = ['category__display_order', 'name']
    
    def get_serializer_class(self):
        """Gebruik verschillende serializers voor list en detail"""
        if self.action == 'list':
            return ServiceListSerializer
        return ServiceDetailSerializer
    
    def get_queryset(self):
        """Pas queryset aan op basis van actie en filters"""
        queryset = super().get_queryset()
        
        # Voor niet-admin gebruikers, toon alleen actieve diensten
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        # Filter op populaire diensten
        popular = self.request.query_params.get('popular', None)
        if popular == 'true':
            queryset = queryset.filter(is_popular=True)
        
        # Filter op uitgelichte diensten
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Filter op online boekbaar
        bookable = self.request.query_params.get('bookable', None)
        if bookable == 'true':
            queryset = queryset.filter(can_book_online=True)
        
        # Filter op spoedservice
        emergency = self.request.query_params.get('emergency', None)
        if emergency == 'true':
            queryset = queryset.filter(has_emergency_service=True)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Log service view bij het ophalen"""
        instance = self.get_object()
        
        # Increment view count
        instance.increment_views()
        
        # Log de view voor analytics
        self._log_service_view(instance, request)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def _log_service_view(self, service, request):
        """Log een dienstweergave"""
        try:
            ServiceView.objects.create(
                service=service,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key or '',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER', '')
            )
        except Exception as e:
            logger.error(f"Error logging service view: {e}")
    
    def _get_client_ip(self, request):
        """Haal client IP adres op"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=True, methods=['post'])
    def increment_quote_request(self, request, slug=None):
        """Increment quote request count (gebruikt door quotes app)"""
        service = self.get_object()
        service.increment_quote_requests()
        return Response({'status': 'quote request count incremented'})
    
    @action(detail=True, methods=['get'])
    def before_after_images(self, request, slug=None):
        """Haal voor/na afbeeldingen op"""
        service = self.get_object()
        
        before_images = service.images.filter(is_before_image=True)
        after_images = service.images.filter(is_after_image=True)
        
        before_serializer = ServiceImageSerializer(before_images, many=True)
        after_serializer = ServiceImageSerializer(after_images, many=True)
        
        return Response({
            'before_images': before_serializer.data,
            'after_images': after_serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def homepage_services(self, request):
        """Haal diensten voor homepage op"""
        # Diensten uit categorieën die op homepage getoond worden
        homepage_categories = ServiceCategory.objects.filter(
            show_on_homepage=True,
            is_active=True
        )
        
        services = Service.objects.filter(
            category__in=homepage_categories,
            is_active=True
        ).select_related('category')[:12]
        
        serializer = ServiceListSerializer(services, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Haal populaire diensten op"""
        popular_services = self.get_queryset().filter(
            is_popular=True,
            is_active=True
        )[:8]
        
        serializer = self.get_serializer(popular_services, many=True)
        return Response(serializer.data)


class ServiceSearchView(generics.ListAPIView):
    """
    Geavanceerde dienst zoekfunctionaliteit
    """
    serializer_class = ServiceListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True)
        search_params = ServiceSearchSerializer(data=self.request.query_params)
        
        if search_params.is_valid():
            data = search_params.validated_data
            
            # Zoek op tekst
            if data.get('q'):
                queryset = queryset.filter(
                    Q(name__icontains=data['q']) |
                    Q(short_description__icontains=data['q']) |
                    Q(full_description__icontains=data['q']) |
                    Q(benefits__icontains=data['q']) |
                    Q(process__icontains=data['q'])
                )
            
            # Filter op categorie
            if data.get('category'):
                queryset = queryset.filter(category__slug=data['category'])
            
            # Filter op vaste prijs
            if data.get('has_fixed_price') is not None:
                queryset = queryset.filter(has_fixed_price=data['has_fixed_price'])
            
            # Filter op online boekbaar
            if data.get('can_book_online') is not None:
                queryset = queryset.filter(can_book_online=data['can_book_online'])
            
            # Filter op spoedservice
            if data.get('has_emergency_service') is not None:
                queryset = queryset.filter(has_emergency_service=data['has_emergency_service'])
            
            # Filter op stad
            if data.get('city'):
                queryset = queryset.filter(areas__city__iexact=data['city'])
            
            # Sortering
            if data.get('sort_by') == 'popular':
                queryset = queryset.order_by('-views_count')
            elif data.get('sort_by') == 'name':
                queryset = queryset.order_by('name')
            elif data.get('sort_by') == 'price_low':
                queryset = queryset.order_by('fixed_price')
            elif data.get('sort_by') == 'price_high':
                queryset = queryset.order_by('-fixed_price')
        
        return queryset.distinct()
    
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


class TestimonialViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor testimonials
    """
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """Filter testimonials op service"""
        queryset = super().get_queryset()
        
        # Voor niet-admin gebruikers, toon alleen goedgekeurde testimonials
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        # Filter op service
        service_slug = self.request.query_params.get('service', None)
        if service_slug:
            queryset = queryset.filter(service__slug=service_slug)
        
        # Filter op uitgelicht
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Sla testimonial op met huidige user"""
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Haal uitgelichte testimonials op"""
        featured_testimonials = self.get_queryset().filter(
            is_featured=True,
            is_approved=True
        )[:6]
        
        serializer = self.get_serializer(featured_testimonials, many=True)
        return Response(serializer.data)


class ServiceStatisticsView(generics.GenericAPIView):
    """
    Statistieken voor diensten
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Haal dienst statistieken op"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Totale statistieken
        total_services = Service.objects.count()
        active_services = Service.objects.filter(is_active=True).count()
        
        # Categorie statistieken
        category_stats = ServiceCategory.objects.annotate(
            service_count=Count('services'),
            active_service_count=Count('services', filter=Q(services__is_active=True))
        ).values('name', 'service_count', 'active_service_count')
        
        # Populaire diensten (top 5)
        popular_services = Service.objects.filter(
            is_active=True
        ).order_by('-views_count')[:5].values('name', 'views_count', 'quote_requests_count')
        
        # Maandelijkse views
        from datetime import datetime, timedelta
        from django.db.models.functions import TruncMonth
        from django.db.models import Count
        
        last_6_months = datetime.now() - timedelta(days=180)
        
        monthly_views = ServiceView.objects.filter(
            created_at__gte=last_6_months
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            views_count=Count('id')
        ).order_by('month')
        
        data = {
            'total_services': total_services,
            'active_services': active_services,
            'category_stats': list(category_stats),
            'popular_services': list(popular_services),
            'monthly_views': list(monthly_views),
        }
        
        return Response(data)