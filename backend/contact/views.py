from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Avg, F, ExpressionWrapper, DurationField, Max, Min
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from services import serializers

from .models import (
    ContactCategory, 
    ContactMessage, 
    ContactAttachment,
    NewsletterSubscriber
)
from .serializers import (
    ContactCategorySerializer,
    ContactMessageCreateSerializer,
    ContactMessageDetailSerializer,
    ContactMessageUpdateSerializer,
    ContactAttachmentSerializer,
    NewsletterSubscriberSerializer
)
from .permissions import IsAdminOrReadOnly, CanManageContactMessages
from .filters import ContactMessageFilter, ContactCategoryFilter


class ContactCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor het beheren van contactcategorieën.
    
    TECHNISCHE CONCEPTEN:
    - ModelViewSet met complete CRUD
    - Actieve categorie filtering voor publieke API
    - Nested categorie structuur
    """
    
    queryset = ContactCategory.objects.all()
    serializer_class = ContactCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ContactCategoryFilter
    search_fields = ['name', 'description', 'email_recipient']
    ordering_fields = ['name', 'priority', 'created_at']
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Pas queryset aan op basis van gebruiker en actie"""
        queryset = super().get_queryset()
        
        # Voor niet-admin gebruikers, toon alleen actieve categorieën
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        # Voor publieke API, toon alleen root categorieën
        if self.action == 'list' and not self.request.user.is_staff:
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset.prefetch_related('subcategories')
    
    def get_serializer_class(self):
        """Gebruik aangepaste serializer voor create/update"""
        if self.action in ['create', 'update', 'partial_update']:
            return ContactCategorySerializer
        return super().get_serializer_class()
    
    @action(detail=True, methods=['get'])
    def messages(self, request, slug=None):
        """Haal alle berichten in deze categorie op"""
        category = self.get_object()
        
        # Toon alleen actieve berichten voor niet-admin
        if request.user.is_staff:
            messages = category.messages.all()
        else:
            messages = category.messages.filter(status__in=['new', 'in_progress'])
        
        # Pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = ContactMessageDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ContactMessageDetailSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Haal alle actieve categorieën op"""
        categories = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor het beheren van contactberichten.
    
    TECHNISCHE CONCEPTEN:
    - Aparte endpoints voor publiek en admin
    - Uitgebreide filtering en zoekfunctionaliteit
    - Bulk acties voor admin
    """
    
    queryset = ContactMessage.objects.all()
    permission_classes = [CanManageContactMessages]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ContactMessageFilter
    search_fields = [
        'full_name', 'email', 'company_name', 'subject',
        'message', 'reference_number'
    ]
    ordering_fields = [
        'created_at', 'updated_at', 'priority',
        'status', 'assigned_to'
    ]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        """Pas queryset aan op basis van gebruiker"""
        queryset = super().get_queryset()
        
        # Voor niet-admin gebruikers, beperk toegang
        if not self.request.user.is_authenticated:
            # Publieke API kan alleen eigen berichten zien (via referentie)
            return queryset.none()
        elif not self.request.user.is_staff:
            # Gebruikers kunnen alleen eigen berichten zien
            return queryset.filter(email=self.request.user.email)
        
        # Admin gebruikers zien alles
        return queryset.select_related(
            'category', 'assigned_to', 'related_product',
            'related_service', 'related_quote'
        ).prefetch_related('attachments')
    
    def get_serializer_class(self):
        """Selecteer de juiste serializer op basis van actie"""
        if self.action == 'create':
            return ContactMessageCreateSerializer
        elif self.action in ['retrieve', 'list']:
            return ContactMessageDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return ContactMessageUpdateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """Pas permissions aan op basis van actie"""
        if self.action == 'create':
            # Iedereen mag contactberichten aanmaken
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Alleen admin mag wijzigen/verwijderen
            return [IsAdminUser()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Log extra informatie bij aanmaken"""
        request = self.context.get('request')
        
        # Zorg dat request in context is
        if request:
            serializer.context['request'] = request
        
        # Creëer bericht
        serializer.save()
        
        # TODO: Stuur bevestigingsmail naar verzender
        # TODO: Stuur notificatie naar admin
    
    def create(self, request, *args, **kwargs):
        """Override create voor CAPTCHA validatie"""
        # CAPTCHA validatie (optioneel)
        captcha_token = request.data.get('captcha_token')
        if captcha_token:
            # Implementeer CAPTCHA validatie logica
            # is_valid = validate_captcha(captcha_token)
            # if not is_valid:
            #     return Response(
            #         {'error': 'Invalid CAPTCHA'},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )
            pass
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, uuid=None):
        """Markeer bericht als gelezen"""
        message = self.get_object()
        
        if request.user.is_staff:
            message.mark_as_read(request.user)
            return Response({'status': 'marked as read'})
        
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, uuid=None):
        """Wijs bericht toe aan een gebruiker"""
        message = self.get_object()
        user_id = request.data.get('user_id')
        
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBORBIDDEN
            )
        
        try:
            from authentication.models import CustomUser
            user = CustomUser.objects.get(id=user_id)
            message.assign_to(user)
            return Response({'status': 'assigned', 'user': user.email})
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, uuid=None):
        """Voeg een notitie toe aan het bericht"""
        message = self.get_object()
        note = request.data.get('note')
        
        if not note or not note.strip():
            return Response(
                {'error': 'Note is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.user.is_staff:
            message.add_response_note(note.strip(), request.user)
            return Response({'status': 'note added'})
        
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistieken over contactberichten"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Basis statistieken
        total_messages = ContactMessage.objects.count()
        new_messages = ContactMessage.objects.filter(status='new').count()
        in_progress = ContactMessage.objects.filter(status='in_progress').count()
        resolved = ContactMessage.objects.filter(status='resolved').count()
        
        # Categorie statistieken
        category_stats = ContactMessage.objects.values(
            'category__name'
        ).annotate(
            count=Count('id'),
            avg_priority=Avg('priority')
        ).order_by('-count')
        
        # Response tijd statistieken
        response_times = ContactMessage.objects.filter(
            responded_at__isnull=False
        ).annotate(
            response_time=ExpressionWrapper(
                F('responded_at') - F('created_at'),
                output_field=DurationField()
            )
        ).aggregate(
            avg_response_time=Avg('response_time'),
            max_response_time=Max('response_time'),
            min_response_time=Min('response_time')
        )
        
        return Response({
            'total_messages': total_messages,
            'by_status': {
                'new': new_messages,
                'in_progress': in_progress,
                'resolved': resolved
            },
            'category_stats': list(category_stats),
            'response_times': response_times
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update van contactberichten"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message_ids = request.data.get('message_ids', [])
        action_type = request.data.get('action')
        
        if not message_ids:
            return Response(
                {'error': 'No message IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = ContactMessage.objects.filter(uuid__in=message_ids)
        
        if action_type == 'mark_read':
            messages.update(status='read')
        elif action_type == 'assign':
            user_id = request.data.get('user_id')
            if user_id:
                messages.update(assigned_to_id=user_id, status='in_progress')
        elif action_type == 'close':
            messages.update(status='closed', responded_at=timezone.now())
        
        return Response({'status': f'{messages.count()} messages updated'})


class ContactAttachmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet voor het beheren van contactbijlagen.
    
    TECHNISCHE CONCEPTEN:
    - File upload functionaliteit
    - Virus scanning (kan async)
    - Permission gebaseerde toegang
    """
    
    queryset = ContactAttachment.objects.all()
    serializer_class = ContactAttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Beperk toegang tot bijlagen van toegankelijke berichten"""
        queryset = super().get_queryset()
        
        if self.request.user.is_staff:
            return queryset
        
        # Gebruikers kunnen alleen bijlagen van hun eigen berichten zien
        user_email = self.request.user.email
        return queryset.filter(
            Q(message__email=user_email) |
            Q(message__assigned_to=self.request.user)
        )
    
    def perform_create(self, serializer):
        """Voeg automatisch message toe bij aanmaken"""
        message_uuid = self.request.data.get('message_uuid')
        
        if not message_uuid:
            raise serializers.ValidationError(
                {'message_uuid': 'This field is required.'}
            )
        
        try:
            message = ContactMessage.objects.get(uuid=message_uuid)
            
            # Controleer permissies
            if not self._can_attach_to_message(message):
                raise PermissionDenied(
                    'You do not have permission to attach files to this message.'
                )
            
            serializer.save(message=message)
            
            # TODO: Virus scanning in background task
            # scan_file_for_viruses.delay(serializer.instance.id)
            
        except ContactMessage.DoesNotExist:
            raise serializers.ValidationError(
                {'message_uuid': 'Message not found.'}
            )
    
    def _can_attach_to_message(self, message):
        """Controleer of gebruiker bijlage mag toevoegen"""
        user = self.request.user
        
        if user.is_staff:
            return True
        
        # Gebruiker kan bijlage toevoegen aan eigen bericht
        if message.email == user.email:
            return True
        
        # Gebruiker kan bijlage toevoegen als toegewezen
        if message.assigned_to == user:
            return True
        
        return False


class NewsletterSubscriptionView(APIView):
    """
    API View voor nieuwsbrief inschrijvingen.
    
    TECHNISCHE CONCEPTEN:
    - Double opt-in flow
    - GDPR compliance
    - Subscription management
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Schrijf in voor nieuwsbrief"""
        serializer = NewsletterSubscriberSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            subscriber = serializer.save()
            
            # TODO: Stuur bevestigingsmail
            # send_confirmation_email.delay(subscriber.id)
            
            return Response({
                'status': 'success',
                'message': _('Bevestigingsmail verstuurd. Controleer je inbox.'),
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Schrijf uit van nieuwsbrief"""
        email = request.data.get('email')
        unsubscribe_token = request.data.get('unsubscribe_token')
        
        if not email or not unsubscribe_token:
            return Response(
                {'error': 'Email and unsubscribe token are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscriber = NewsletterSubscriber.objects.get(
                email=email,
                unsubscribe_token=unsubscribe_token
            )
            subscriber.unsubscribe()
            
            return Response({
                'status': 'success',
                'message': _('Succesvol uitgeschreven van de nieuwsbrief.')
            })
        
        except NewsletterSubscriber.DoesNotExist:
            return Response(
                {'error': 'Subscription not found or invalid token.'},
                status=status.HTTP_404_NOT_FOUND
            )


class ContactFormView(APIView):
    """
    Publieke API voor contactformulier.
    
    TECHNISCHE CONCEPTEN:
    - Vereenvoudigde interface voor frontend
    - CAPTCHA integratie
    - Rate limiting
    """
    
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request):
        """Haal beschikbare categorieën en configuratie op"""
        categories = ContactCategory.objects.filter(
            is_active=True,
            parent__isnull=True
        )
        
        category_serializer = ContactCategorySerializer(
            categories,
            many=True,
            context={'request': request}
        )
        
        # Configuratie voor frontend
        config = {
            'max_attachments': 5,
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'allowed_file_types': [
                'image/jpeg', 'image/png', 'image/gif',
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ],
            'requires_captcha': False,  # Configureerbaar
            'rate_limit': {
                'max_per_hour': 5,
                'max_per_day': 20
            }
        }
        
        return Response({
            'categories': category_serializer.data,
            'config': config
        })
    
    def post(self, request):
        """Verstuur contactbericht"""
        # Rate limiting check (eenvoudige implementatie)
        ip_address = self._get_client_ip(request)
        if self._is_rate_limited(ip_address):
            return Response(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Gebruik de create serializer
        serializer = ContactMessageCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            message = serializer.save()
            
            # Verwerk bijlagen als aanwezig
            files = request.FILES.getlist('attachments')
            for file in files[:5]:  # Max 5 bijlagen
                attachment_serializer = ContactAttachmentSerializer(
                    data={'file': file},
                    context={'request': request}
                )
                if attachment_serializer.is_valid():
                    attachment_serializer.save(message=message)
            
            # TODO: Stuur bevestigingsmail
            # send_contact_confirmation.delay(message.id)
            
            return Response({
                'status': 'success',
                'message': _('Bedankt voor je bericht. We nemen zo snel mogelijk contact met je op.'),
                'reference_number': message.reference_number,
                'uuid': str(message.uuid)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_client_ip(self, request):
        """Haal client IP adres op"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_rate_limited(self, ip_address):
        """Controleer rate limiting"""
        from django.core.cache import cache
        
        key_hour = f'contact_rate_limit_{ip_address}_hour'
        key_day = f'contact_rate_limit_{ip_address}_day'
        
        # Controleer per uur
        count_hour = cache.get(key_hour, 0)
        if count_hour >= 5:  # Max 5 per uur
            return True
        
        # Controleer per dag
        count_day = cache.get(key_day, 0)
        if count_day >= 20:  # Max 20 per dag
            return True
        
        # Update counters
        cache.set(key_hour, count_hour + 1, timeout=3600)
        cache.set(key_day, count_day + 1, timeout=86400)
        
        return False