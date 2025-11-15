from rest_framework.permissions import BasePermission


class RoleHasPermission(BasePermission):
    """
    Check if user's role has the required permission(s).
    Use `required_role_permissions = ["code1", "code2"]` on your view.
    """

    def has_permission(self, request, view):
        required_permissions = getattr(view, "required_role_permissions", [])
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if not hasattr(user, "role") or not user.role:
            return False

        role_permissions = set(
            p.code for p in user.role.permissions.filter(is_active=True)
        )
        return all(perm in role_permissions for perm in required_permissions)
