import os

from django.conf import settings
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeRedirectView,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)


v1_router = DefaultRouter()
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        's/<int:pk>/',
        RecipeRedirectView.as_view({'get': 'link_redirect'}),
        name='short-link'
    ),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    re_path(
        r'^openapi-schema\.yml$',
        serve,
        kwargs={
            'path': 'openapi-schema.yml',
            'document_root': os.path.join(settings.BASE_DIR, 'docs')
        }
    ),
]

