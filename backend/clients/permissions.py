from rest_framework import permissions


class IsClientOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a client or admins to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or admin
        return obj.created_by == request.user or request.user.is_staff


class IsContactOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a client contact or admins to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the client owner or admin
        return obj.client.created_by == request.user or request.user.is_staff


class IsAddressOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a client address or admins to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the client owner or admin
        return obj.client.created_by == request.user or request.user.is_staff