from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import (
    Order, OrderItem, Payment, 
    OrderTag, OrderAttachment, OrderHistory
)
from .serializers import (
    OrderListSerializer, OrderDetailSerializer,
    OrderCreateSerializer, OrderUpdateSerializer,
    OrderItemSerializer, PaymentSerializer,
    OrderTagSerializer, OrderAttachmentSerializer,
    OrderHistorySerializer
)
from .permissions import CanManageOrders, IsOrderOwnerOrAdmin
from .filters import OrderFilter


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor het beheren van orders.
    
    TECHNISCHE CONCEPTEN:
    - Complete order management
    - Status workflow management
    - Payment integration
    - Advanced filtering and search
    """
    
    queryset = Order.objects.all()
    permission_classes = [CanManageOrders]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = [
        'order_number', 'reference', 'client__company_name',
        'client__email', 'tracking_number', 'internal_notes'
    ]
    ordering_fields = [
        'order_number', 'created_at', 'delivery_date',
        'total_incl_tax', 'status', 'priority'
    ]
    
    def get_queryset(self):
        """Pas queryset aan op basis van gebruiker"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_authenticated:
            return queryset.none()
        
        # Admin ziet alles
        if self.request.user.is_staff:
            return queryset.select_related(
                'client', 'contact_person', 'quote',
                'delivery_address', 'billing_address',
                'assigned_to', 'project'
            ).prefetch_related(
                'items', 'payments', 'tags',
                'attachments', 'history'
            )
        
        # Gebruiker ziet alleen eigen orders
        return queryset.filter(
            Q(client__assigned_to=self.request.user) |
            Q(assigned_to=self.request.user) |
            Q(created_by=self.request.user)
        ).distinct()
    
    def get_serializer_class(self):
        """Selecteer de juiste serializer"""
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        else:
            return OrderListSerializer
    
    def get_permissions(self):
        """Pas permissions aan op basis van actie"""
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Log extra informatie bij aanmaak"""
        serializer.save(created_by=self.request.user)
        
        # Log geschiedenis
        OrderHistory.objects.create(
            order=serializer.instance,
            action='created',
            changed_by=self.request.user,
            notes='Order aangemaakt'
        )
        
        # TODO: Stuur notificatie naar betrokkenen
    
    def perform_update(self, serializer):
        """Log extra informatie bij update"""
        old_instance = self.get_object()
        old_status = old_instance.status
        
        serializer.save()
        
        # Check voor status wijziging
        if old_status != serializer.instance.status:
            OrderHistory.objects.create(
                order=serializer.instance,
                action='status_changed',
                old_value=old_status,
                new_value=serializer.instance.status,
                changed_by=self.request.user,
                notes=f'Status gewijzigd van {old_status} naar {serializer.instance.status}'
            )
            
            # TODO: Trigger status-specifieke acties
            # self._handle_status_change(serializer.instance, old_status)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Bevestig de order"""
        order = self.get_object()
        
        if order.confirm():
            return Response({'status': 'confirmed'})
        
        return Response(
            {'error': _('Order kan niet worden bevestigd')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def start_processing(self, request, pk=None):
        """Start verwerking van order"""
        order = self.get_object()
        
        if order.start_processing():
            return Response({'status': 'processing_started'})
        
        return Response(
            {'error': _('Order kan niet in verwerking worden genomen')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def mark_as_shipped(self, request, pk=None):
        """Markeer order als verzonden"""
        order = self.get_object()
        tracking_number = request.data.get('tracking_number', '')
        
        if order.mark_as_shipped(tracking_number):
            return Response({'status': 'shipped'})
        
        return Response(
            {'error': _('Order kan niet als verzonden worden gemarkeerd')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def mark_as_delivered(self, request, pk=None):
        """Markeer order als afgeleverd"""
        order = self.get_object()
        
        if order.mark_as_delivered():
            return Response({'status': 'delivered'})
        
        return Response(
            {'error': _('Order kan niet als afgeleverd worden gemarkeerd')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuleer de order"""
        order = self.get_object()
        reason = request.data.get('reason', '')
        
        if order.cancel(reason):
            return Response({'status': 'cancelled'})
        
        return Response(
            {'error': _('Order kan niet worden geannuleerd')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Markeer order als voltooid"""
        order = self.get_object()
        
        if order.complete():
            return Response({'status': 'completed'})
        
        return Response(
            {'error': _('Order kan niet als voltooid worden gemarkeerd')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Haal alle items van deze order op"""
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Haal alle betalingen van deze order op"""
        order = self.get_object()
        payments = order.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Haal geschiedenis van deze order op"""
        order = self.get_object()
        history = order.history.all()
        serializer = OrderHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistieken over orders"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Totaal statistieken
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(
            total=Sum('total_incl_tax')
        )['total'] or Decimal('0.00')
        
        # Status statistieken
        status_stats = Order.objects.values('status').annotate(
            count=Count('id'),
            total_value=Sum('total_incl_tax')
        ).order_by('-count')
        
        # Maandelijkse statistieken
        from django.db.models.functions import TruncMonth
        monthly_stats = Order.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            total_value=Sum('total_incl_tax')
        ).order_by('-month')[:12]
        
        # Klant statistieken
        client_stats = Order.objects.values('client__company_name').annotate(
            count=Count('id'),
            total_value=Sum('total_incl_tax')
        ).order_by('-total_value')[:10]
        
        return Response({
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'status_stats': list(status_stats),
            'monthly_stats': list(monthly_stats),
            'top_clients': list(client_stats),
        })
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard statistieken"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        week_ago = today - timezone.timedelta(days=7)
        month_ago = today - timezone.timedelta(days=30)
        
        # Recente orders
        recent_orders = Order.objects.filter(
            created_at__gte=week_ago
        ).order_by('-created_at')[:10]
        
        # Achterstallige betalingen
        overdue_orders = Order.objects.filter(
            payment_status='overdue',
            payment_due_date__lt=today
        ).count()
        
        # Orders in verwerking
        processing_orders = Order.objects.filter(
            status__in=['processing', 'ready_for_shipment']
        ).count()
        
        # Orders voor vandaag
        todays_deliveries = Order.objects.filter(
            delivery_date__date=today,
            status__in=['confirmed', 'processing', 'ready_for_shipment', 'shipped']
        ).count()
        
        serializer = OrderListSerializer(recent_orders, many=True)
        
        return Response({
            'recent_orders': serializer.data,
            'overdue_orders': overdue_orders,
            'processing_orders': processing_orders,
            'todays_deliveries': todays_deliveries,
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update van orders"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order_ids = request.data.get('order_ids', [])
        action_type = request.data.get('action')
        
        if not order_ids:
            return Response(
                {'error': 'No order IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orders = Order.objects.filter(id__in=order_ids)
        
        if action_type == 'confirm':
            for order in orders:
                order.confirm()
        elif action_type == 'start_processing':
            for order in orders:
                order.start_processing()
        elif action_type == 'assign':
            user_id = request.data.get('user_id')
            if user_id:
                from authentication.models import CustomUser
                try:
                    user = CustomUser.objects.get(id=user_id)
                    orders.update(assigned_to=user)
                except CustomUser.DoesNotExist:
                    return Response(
                        {'error': 'User not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
        
        return Response({'status': f'{orders.count()} orders updated'})


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor order items.
    """
    
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """Beperk toegang tot items van toegankelijke orders"""
        queryset = super().get_queryset()
        
        if self.request.user.is_staff:
            return queryset.select_related('order', 'product', 'service')
        
        # Gebruiker kan alleen items van toegankelijke orders zien
        return queryset.filter(
            Q(order__client__assigned_to=self.request.user) |
            Q(order__assigned_to=self.request.user) |
            Q(order__created_by=self.request.user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """Markeer (deel van) item als afgeleverd"""
        item = self.get_object()
        quantity = request.data.get('quantity')
        
        try:
            if quantity:
                quantity = Decimal(quantity)
            else:
                quantity = None
            
            if item.mark_as_delivered(quantity):
                return Response({'status': 'delivered'})
            
            return Response(
                {'error': _('Item kan niet als afgeleverd worden gemarkeerd')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except (ValueError, TypeError):
            return Response(
                {'error': _('Ongeldige hoeveelheid')},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor betalingen.
    """
    
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Beperk toegang tot betalingen van toegankelijke orders"""
        queryset = super().get_queryset()
        
        if self.request.user.is_staff:
            return queryset.select_related('order')
        
        # Gebruiker kan alleen betalingen van toegankelijke orders zien
        return queryset.filter(
            Q(order__client__assigned_to=self.request.user) |
            Q(order__assigned_to=self.request.user) |
            Q(order__created_by=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        """Creëer betaling"""
        payment = serializer.save()
        
        # Log geschiedenis
        OrderHistory.objects.create(
            order=payment.order,
            action='payment_received',
            changed_by=self.request.user,
            notes=f'Betaling ontvangen: €{payment.amount}'
        )
        
        # TODO: Stuur betalingsbevestiging


class OrderTagViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor order tags.
    """
    
    queryset = OrderTag.objects.filter(is_active=True)
    serializer_class = OrderTagSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filter op actieve tags"""
        return super().get_queryset().order_by('name')


class OrderAttachmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor order bijlagen.
    """
    
    queryset = OrderAttachment.objects.all()
    serializer_class = OrderAttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Beperk toegang tot bijlagen van toegankelijke orders"""
        queryset = super().get_queryset()
        
        if self.request.user.is_staff:
            return queryset
        
        # Gebruiker kan alleen bijlagen van toegankelijke orders zien
        return queryset.filter(
            Q(order__client__assigned_to=self.request.user) |
            Q(order__assigned_to=self.request.user) |
            Q(order__created_by=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        """Voeg automatisch order en uploader toe"""
        order_id = self.request.data.get('order_id')
        
        if not order_id:
            raise serializers.ValidationError(
                {'order_id': 'This field is required.'}
            )
        
        try:
            order = Order.objects.get(id=order_id)
            
            # Controleer permissies
            if not self._can_attach_to_order(order):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    'You do not have permission to attach files to this order.'
                )
            
            serializer.save(
                order=order,
                uploaded_by=self.request.user
            )
            
            # Log geschiedenis
            OrderHistory.objects.create(
                order=order,
                action='attachment_added',
                changed_by=self.request.user,
                notes=f'Bijlage toegevoegd: {serializer.instance.name}'
            )
            
        except Order.DoesNotExist:
            raise serializers.ValidationError(
                {'order_id': 'Order not found.'}
            )
    
    def _can_attach_to_order(self, order):
        """Controleer of gebruiker bijlage mag toevoegen"""
        user = self.request.user
        
        if user.is_staff:
            return True
        
        if order.client.assigned_to == user:
            return True
        
        if order.assigned_to == user:
            return True
        
        if order.created_by == user:
            return True
        
        return False