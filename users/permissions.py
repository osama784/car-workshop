from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not permissions.IsAuthenticated().has_permission(request, view):
            return False
        return True
        
    def has_object_permission(self, request, view, obj):
        if request.user.customer == obj:
            return True
        return False    