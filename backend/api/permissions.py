from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    GET-запросы доступны всем пользователям;
    POST-запросы доступны только аутентифицированным пользователям;
    PATCH и DELETE-запросы доступны автору.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            obj.author == request.user
        )
