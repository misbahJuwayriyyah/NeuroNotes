from typing import Any
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to admin users (role='admin').
    """

    def has_permission(self, request, view)-> Any:
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")


class IsAdminOrOwner(permissions.BasePermission):
    """
    Allow full access to admins, but only object-level access for owners (researchers).
    """

    def has_object_permission(self, request, view, obj):# -> Any | Literal[True]:
        # Admins can do anything
        if request.user.role == "admin":
            return True

        # Otherwise, only owner can view/update/delete their own object
        return obj.owner == request.user
