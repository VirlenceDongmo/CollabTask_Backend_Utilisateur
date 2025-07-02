from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Seulement pour les administrateurs"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsOwnerOrAdmin(permissions.BasePermission):
    """Autorise le propriétaire ou l'admin"""
    def has_object_permission(self, request, view, obj):
        # Si l'utilisateur est admin
        if request.user.role == 'ADMIN':
            return True
        # Si l'objet a une relation 'user' ou 'owner'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False

class IsSameUserOrAdmin(permissions.BasePermission):
    """Pour les opérations sur les utilisateurs"""
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'ADMIN' or obj == request.user