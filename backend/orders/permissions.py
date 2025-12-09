from rest_framework import permissions
from django.utils.translation import gettext_lazy as _
from .models import Order


class CanManageOrders(permissions.BasePermission):
    """
    Permission class voor order management.
    
    TECHNISCHE CONCEPTEN:
    - Role-based access control
    - Object-level permissions
    - Business logic integration
    """
    
    def has_permission(self, request, view):
        # Iedereen mag orders aanmaken (authenticated users)
        if view.action == 'create':
            return request.user.is_authenticated
        
        # Voor overige acties moet gebruiker geauthenticeerd zijn
        if not request.user.is_authenticated:
            return False
        
        # Admin heeft volledige toegang
        if request.user.is_staff:
            return True
        
        # Verkopers/accountmanagers kunnen orders van hun klanten zien
        return view.action in ['list', 'retrieve', 'items', 'payments', 'history']
    
    def has_object_permission(self, request, view, obj):
        # Admin heeft volledige toegang
        if request.user.is_staff:
            return True
        
        # Accountmanager kan orders van zijn/haar klanten zien
        if hasattr(obj, 'client') and obj.client.assigned_to == request.user:
            return view.action in ['retrieve', 'items', 'payments', 'history']
        
        # Toegewezen medewerker kan de order zien
        if obj.assigned_to == request.user:
            return view.action in ['retrieve', 'items', 'payments', 'history']
        
        # Aangemaakt door gebruiker
        if obj.created_by == request.user:
            return view.action in ['retrieve', 'items', 'payments', 'history']
        
        return False


class IsOrderOwnerOrAdmin(permissions.BasePermission):
    """
    Permission voor order eigenaar of admin.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Check verschillende ownership scenarios
        if hasattr(obj, 'order'):
            order = obj.order
        else:
            order = obj
        
        if order.client.assigned_to == request.user:
            return True
        
        if order.assigned_to == request.user:
            return True
        
        if order.created_by == request.user:
            return True
        
        return False