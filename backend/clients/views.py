import csv
import json
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from .models import Client, ClientContact, Address
from .serializers import (
    ClientSerializer, 
    ClientListSerializer,
    ClientContactSerializer,
    AddressSerializer,
    ClientExportSerializer
)
from .permissions import IsClientOwnerOrAdmin, IsContactOwnerOrAdmin, IsAddressOwnerOrAdmin
import logging

logger = logging.getLogger(__name__)


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Client instances.
    """
    queryset = Client.objects.all().order_by('-created_at')
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'company_name', 'email', 'phone', 'vat_number', 'industry']
    ordering_fields = ['name', 'company_name', 'created_at', 'updated_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter clients based on user permissions.
        Admins see all clients, regular users see their own clients.
        """
        user = self.request.user
        
        queryset = Client.objects.all()
        
        # Apply filters from query parameters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        client_type = self.request.query_params.get('type')
        if client_type:
            queryset = queryset.filter(client_type=client_type)
        
        industry = self.request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(industry=industry)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        created_after = self.request.query_params.get('created_after')
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
        
        created_before = self.request.query_params.get('created_before')
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(notes__icontains=search)
            )
        
        # If user is not admin, filter by ownership
        if not user.is_staff:
            # Assuming clients have a created_by field
            queryset = queryset.filter(created_by=user)
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializer for list view"""
        if self.action == 'list':
            return ClientListSerializer
        return ClientSerializer
    
    def get_permissions(self):
        """
        Custom permissions for different actions.
        """
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsClientOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set created_by user"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by user"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def quotes(self, request, pk=None):
        """Get all quotes for this client"""
        client = self.get_object()
        from quotes.serializers import QuoteListSerializer  # Import here to avoid circular import
        quotes = client.quotes.all().order_by('-created_at')
        serializer = QuoteListSerializer(quotes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate/deactivate client"""
        client = self.get_object()
        client.is_active = not client.is_active
        client.save()
        
        action = "activated" if client.is_active else "deactivated"
        return Response({
            "message": f"Client {action} successfully",
            "is_active": client.is_active
        })
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate client with contacts and addresses"""
        client = self.get_object()
        
        # Duplicate client
        client.pk = None
        client.name = f"{client.name} (Copy)"
        client.save()
        
        # Duplicate contacts
        for contact in client.contacts.all():
            contact.pk = None
            contact.client = client
            contact.save()
        
        # Duplicate addresses
        for address in client.addresses.all():
            address.pk = None
            address.client = client
            address.save()
        
        serializer = self.get_serializer(client)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Get client activity timeline"""
        client = self.get_object()
        timeline = []
        
        # Add client creation
        timeline.append({
            'date': client.created_at,
            'type': 'client_created',
            'title': 'Client Created',
            'description': f"Client '{client.name}' was created"
        })
        
        # Add quote events
        for quote in client.quotes.all():
            timeline.append({
                'date': quote.created_at,
                'type': 'quote_created',
                'title': 'Quote Created',
                'description': f"Quote '{quote.quote_number}' was created",
                'quote_id': quote.id,
                'quote_number': quote.quote_number
            })
            
            if quote.sent_date:
                timeline.append({
                    'date': quote.sent_date,
                    'type': 'quote_sent',
                    'title': 'Quote Sent',
                    'description': f"Quote '{quote.quote_number}' was sent to client",
                    'quote_id': quote.id,
                    'quote_number': quote.quote_number
                })
            
            if quote.accepted_date:
                timeline.append({
                    'date': quote.accepted_date,
                    'type': 'quote_accepted',
                    'title': 'Quote Accepted',
                    'description': f"Quote '{quote.quote_number}' was accepted",
                    'quote_id': quote.id,
                    'quote_number': quote.quote_number
                })
        
        # Sort by date descending
        timeline.sort(key=lambda x: x['date'], reverse=True)
        
        return Response(timeline)


class ClientContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing ClientContact instances.
    Nested under clients.
    """
    serializer_class = ClientContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter contacts for specific client"""
        client_pk = self.kwargs.get('client_pk')
        return ClientContact.objects.filter(client_id=client_pk).order_by('-is_primary_contact', 'first_name')
    
    def get_serializer_context(self):
        """Add client_id to serializer context"""
        context = super().get_serializer_context()
        context['client_id'] = self.kwargs.get('client_pk')
        return context
    
    def get_permissions(self):
        """Custom permissions"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsContactOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Save with client from URL"""
        client_pk = self.kwargs.get('client_pk')
        client = Client.objects.get(pk=client_pk)
        serializer.save(client=client)
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, client_pk=None, pk=None):
        """Set this contact as primary contact"""
        contact = self.get_object()
        
        # Remove primary status from all other contacts for this client
        ClientContact.objects.filter(client_id=client_pk).update(is_primary_contact=False)
        
        # Set this contact as primary
        contact.is_primary_contact = True
        contact.save()
        
        return Response({
            "message": f"Contact '{contact.first_name} {contact.last_name}' set as primary contact",
            "is_primary_contact": contact.is_primary_contact
        })


class AddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Address instances.
    Nested under clients.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter addresses for specific client"""
        client_pk = self.kwargs.get('client_pk')
        return Address.objects.filter(client_id=client_pk).order_by('-is_primary', 'address_type')
    
    def get_permissions(self):
        """Custom permissions"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAddressOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Save with client from URL"""
        client_pk = self.kwargs.get('client_pk')
        client = Client.objects.get(pk=client_pk)
        serializer.save(client=client)
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, client_pk=None, pk=None):
        """Set this address as primary address"""
        address = self.get_object()
        
        # Remove primary status from all other addresses for this client
        Address.objects.filter(client_id=client_pk).update(is_primary=False)
        
        # Set this address as primary
        address.is_primary = True
        address.save()
        
        return Response({
            "message": f"Address set as primary",
            "is_primary": address.is_primary
        })


class ClientStatsView(APIView):
    """
    View for client statistics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        queryset = Client.objects.all()
        
        if not user.is_staff:
            queryset = queryset.filter(created_by=user)
        
        total_clients = queryset.count()
        active_clients = queryset.filter(is_active=True).count()
        inactive_clients = queryset.filter(is_active=False).count()
        
        # Clients by type
        clients_by_type = queryset.values('client_type').annotate(
            count=Count('id')
        ).order_by('client_type')
        
        # Clients by status
        clients_by_status = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Clients by industry
        clients_by_industry = queryset.exclude(industry='').values('industry').annotate(
            count=Count('id')
        ).order_by('-count')[:10]  # Top 10 industries
        
        # Monthly growth
        six_months_ago = timezone.now() - timezone.timedelta(days=180)
        monthly_growth = queryset.filter(
            created_at__gte=six_months_ago
        ).extra({
            'month': "date_trunc('month', created_at)"
        }).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Clients with most quotes
        top_clients = queryset.annotate(
            quote_count=Count('quotes')
        ).filter(quote_count__gt=0).order_by('-quote_count')[:5]
        
        top_clients_data = []
        for client in top_clients:
            top_clients_data.append({
                'id': client.id,
                'name': client.name,
                'quote_count': client.quote_count
            })
        
        return Response({
            'total_clients': total_clients,
            'active_clients': active_clients,
            'inactive_clients': inactive_clients,
            'clients_by_type': list(clients_by_type),
            'clients_by_status': list(clients_by_status),
            'top_industries': list(clients_by_industry),
            'monthly_growth': list(monthly_growth),
            'top_clients': top_clients_data,
        })


class ClientExportView(APIView):
    """
    View for exporting clients to CSV or JSON.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        format_type = request.query_params.get('format', 'json')
        user = request.user
        queryset = Client.objects.all()
        
        if not user.is_staff:
            queryset = queryset.filter(created_by=user)
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        client_type = request.query_params.get('type')
        if client_type:
            queryset = queryset.filter(client_type=client_type)
        
        industry = request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(industry=industry)
        
        serializer = ClientExportSerializer(queryset, many=True)
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="clients_export.csv"'
            
            writer = csv.writer(response)
            
            # Write header
            writer.writerow([
                'ID', 'Name', 'Company Name', 'Email', 'Phone', 'Website',
                'VAT Number', 'Registration Number', 'Industry', 'Type',
                'Status', 'Payment Terms', 'Credit Limit', 'Discount %',
                'Active', 'Created At'
            ])
            
            # Write data
            for client in serializer.data:
                writer.writerow([
                    client['id'],
                    client['name'],
                    client['company_name'],
                    client['email'],
                    client['phone'],
                    client['website'],
                    client['vat_number'],
                    client['registration_number'],
                    client['industry'],
                    client['client_type'],
                    client['status'],
                    client['payment_terms'],
                    client['credit_limit'],
                    client['discount_percentage'],
                    'Yes' if client['is_active'] else 'No',
                    client['created_at'],
                ])
            
            return response
        
        else:  # JSON format
            return Response(serializer.data)


class ClientImportView(APIView):
    """
    View for importing clients from CSV or JSON.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    
    def post(self, request):
        file = request.FILES.get('file')
        data = request.data.get('data')
        
        if not file and not data:
            return Response(
                {"error": "No file or data provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        imported_count = 0
        errors = []
        
        try:
            if file:
                # Handle CSV file
                if file.name.endswith('.csv'):
                    decoded_file = file.read().decode('utf-8').splitlines()
                    reader = csv.DictReader(decoded_file)
                    
                    for row in reader:
                        try:
                            client_data = {
                                'name': row.get('Name') or row.get('name'),
                                'company_name': row.get('Company Name') or row.get('company_name'),
                                'email': row.get('Email') or row.get('email'),
                                'phone': row.get('Phone') or row.get('phone'),
                                'client_type': row.get('Type') or row.get('client_type') or 'individual',
                                'status': row.get('Status') or row.get('status') or 'active',
                                'is_active': row.get('Active') or row.get('is_active') or True,
                            }
                            
                            # Clean boolean values
                            if isinstance(client_data['is_active'], str):
                                client_data['is_active'] = client_data['is_active'].lower() in ['yes', 'true', '1']
                            
                            serializer = ClientSerializer(data=client_data, context={'request': request})
                            if serializer.is_valid():
                                serializer.save(created_by=request.user)
                                imported_count += 1
                            else:
                                errors.append({
                                    'row': row,
                                    'errors': serializer.errors
                                })
                        
                        except Exception as e:
                            errors.append({
                                'row': row,
                                'error': str(e)
                            })
                
                # Handle JSON file
                elif file.name.endswith('.json'):
                    import json
                    data = json.loads(file.read().decode('utf-8'))
                    return self._import_json_data(data, request.user)
            
            elif data:
                # Handle JSON data
                return self._import_json_data(data, request.user)
        
        except Exception as e:
            return Response(
                {"error": f"Import failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "message": f"Successfully imported {imported_count} clients",
            "imported_count": imported_count,
            "errors": errors if errors else None
        })
    
    def _import_json_data(self, data, user):
        """Helper method to import JSON data"""
        imported_count = 0
        errors = []
        
        if isinstance(data, dict):
            data = [data]  # Convert single object to list
        
        for item in data:
            try:
                serializer = ClientSerializer(data=item, context={'request': {'user': user}})
                if serializer.is_valid():
                    serializer.save(created_by=user)
                    imported_count += 1
                else:
                    errors.append({
                        'item': item,
                        'errors': serializer.errors
                    })
            except Exception as e:
                errors.append({
                    'item': item,
                    'error': str(e)
                })
        
        return Response({
            "message": f"Successfully imported {imported_count} clients",
            "imported_count": imported_count,
            "errors": errors if errors else None
        })


class ClientSearchView(generics.ListAPIView):
    """
    View for searching clients with advanced filters.
    """
    serializer_class = ClientListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Client.objects.all()
        
        if not user.is_staff:
            queryset = queryset.filter(created_by=user)
        
        # Search query
        query = self.request.query_params.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(company_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query) |
                Q(vat_number__icontains=query)
            )
        
        return queryset[:20]  # Limit results


class ClientBulkDeleteView(APIView):
    """
    View for bulk deleting clients.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        client_ids = request.data.get('client_ids', [])
        
        if not client_ids:
            return Response(
                {"error": "No client IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        user = request.user
        queryset = Client.objects.filter(id__in=client_ids)
        
        if not user.is_staff:
            queryset = queryset.filter(created_by=user)
        
        # Check if all requested clients can be deleted
        if queryset.count() != len(client_ids):
            return Response(
                {"error": "Some clients not found or you don't have permission"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Delete clients
        count = queryset.count()
        queryset.delete()
        
        return Response({
            "message": f"Successfully deleted {count} clients",
            "deleted_count": count
        })


class IndustryListView(APIView):
    """
    View to get list of all industries.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        queryset = Client.objects.all()
        
        if not user.is_staff:
            queryset = queryset.filter(created_by=user)
        
        industries = queryset.exclude(
            Q(industry__isnull=True) | Q(industry='')
        ).values_list('industry', flat=True).distinct().order_by('industry')
        
        return Response(list(industries))