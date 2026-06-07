from rest_framework import permissions

from account.models import User

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            return obj == request.user
        return obj.user == request.user
