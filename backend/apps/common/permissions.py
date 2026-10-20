from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """Allows access only to users with the ADMIN role or superusers."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'ADMIN' or request.user.is_superuser)
        )

class IsHODRole(BasePermission):
    """Allows access only to users with the HOD role."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'HOD' or request.user.is_superuser)
        )

class IsFacultyRole(BasePermission):
    """Allows access only to users with the FACULTY role."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'FACULTY'
        )

class IsHODOrAdminRole(BasePermission):
    """Allows access to HOD or Admin roles."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role in ['ADMIN', 'HOD'] or request.user.is_superuser)
        )

class IsFacultyOrHODOrAdminRole(BasePermission):
    """Allows access to any valid staff role."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role in ['ADMIN', 'HOD', 'FACULTY'] or request.user.is_superuser)
        )
