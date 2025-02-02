from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """ Custom permission to only allow owners of an object to edit it."""
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "admin":
            return True
        return obj.creted_by  == request.user

class IsOwnerOrReadOnlyTransaction(BasePermission):
    """ Custom permission to only allow owners of an object to edit it."""
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "admin":
            return True
        return obj.user  == request.user



class IsDepartmentUser(BasePermission):
    """
    Allows access to users who are department members.
    """
    def has_permission(self, request, view):
        return request.user and request.user.user_type in ['ted', 's2l']
