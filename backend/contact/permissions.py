from rest_framework import permissions
from django.utils.translation import gettext_lazy as _


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin-only write access, read access voor iedereen.
    
    TECHNISCHE CONCEPTEN:
    - HTTP method checking
    - User role validation
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff


class CanManageContactMessages(permissions.BasePermission):
    """
    Permission class voor contactbericht management.
    
    TECHNISCHE CONCEPTEN:
    - Role-based access control
    - Object-level permissions
    """
    
    def has_permission(self, request, view):
        # Iedereen mag berichten aanmaken
        if view.action == 'create':
            return True
        
        # Voor overige acties moet gebruiker geauthenticeerd zijn
        if not request.user.is_authenticated:
            return False
        
        # Admin heeft volledige toegang
        if request.user.is_staff:
            return True
        
        # Gebruiker mag alleen eigen berichten zien
        return view.action in ['list', 'retrieve']
    
    def has_object_permission(self, request, view, obj):
        # Admin heeft volledige toegang
        if request.user.is_staff:
            return True
        
        # Gebruiker mag alleen eigen berichten zien
        if hasattr(obj, 'email'):
            return obj.email == request.user.email
        
        # Voor bijlagen, controleer toegang via bericht
        if hasattr(obj, 'message'):
            return self.has_object_permission(request, view, obj.message)
        
        return False