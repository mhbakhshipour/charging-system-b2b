from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        if hasattr(obj, "user"):
            owner = obj.user
        elif hasattr(obj, "owner"):
            owner = obj.owner
        elif hasattr(obj, "creator"):
            owner = obj.creator
        else:
            raise ValueError("This object has no any user field")

        return (owner == request.user) or request.user.is_superuser
