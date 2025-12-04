from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Alleen admin gebruikers kunnen schrijven, anderen alleen lezen
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Alleen de eigenaar kan objecten bewerken
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Voor testimonials, user is niet altijd ingevuld
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return request.user and request.user.is_staff