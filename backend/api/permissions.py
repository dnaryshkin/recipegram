from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthorOrReadOnly(BasePermission):
    """
    GET-запросы доступны всем пользователям;
    POST-запросы доступны только аутентифицированным пользователям;
    PATCH и DELETE-запросы доступны автору, модератору или администратору.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            obj.author == request.user
        )