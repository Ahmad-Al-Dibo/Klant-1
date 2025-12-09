# quotes/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from .models import QuoteDocument
from .serializers import QuoteDocumentSerializer, QuoteDocumentListSerializer
import os


class QuoteDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing quote documents"""
    queryset = QuoteDocument.objects.all()
    serializer_class = QuoteDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter documents based on user permissions"""
        queryset = QuoteDocument.objects.all()
        
        # If quote_id is provided in query params
        quote_id = self.request.query_params.get('quote_id')
        if quote_id:
            queryset = queryset.filter(quote_id=quote_id)
        
        # If user is not admin, only show documents for their quotes
        if not self.request.user.is_staff:
            queryset = queryset.filter(quote__created_by=self.request.user)
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializer for list view"""
        if self.action == 'list':
            return QuoteDocumentListSerializer
        return QuoteDocumentSerializer
    
    def perform_create(self, serializer):
        """Set created_by user"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by user"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download document file"""
        document = self.get_object()
        
        if not document.file:
            raise Http404("File not found")
        
        if not os.path.exists(document.file.path):
            raise Http404("File does not exist on server")
        
        # Check permissions
        if not request.user.is_staff and document.quote.created_by != request.user:
            return Response(
                {"error": "You don't have permission to download this document"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Open and serve file
        response = FileResponse(
            open(document.file.path, 'rb'),
            content_type=document.mime_type
        )
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(document.file.name)}"'
        return response
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete documents"""
        document_ids = request.data.get('document_ids', [])
        
        if not document_ids:
            return Response(
                {"error": "No document IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter documents user has permission to delete
        queryset = self.get_queryset()
        documents = queryset.filter(id__in=document_ids)
        
        if len(documents) != len(document_ids):
            return Response(
                {"error": "Some documents not found or you don't have permission"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        count = documents.count()
        documents.delete()
        
        return Response({
            "message": f"Successfully deleted {count} documents",
            "deleted_count": count
        })