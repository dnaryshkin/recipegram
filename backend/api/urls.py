from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
    RecipeRedirectView,
)


v1_router = DefaultRouter()
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        's/<str:short_link>/',
        RecipeRedirectView.as_view({'get': 'link_redirect'}),
        name='link_redirect'
    ),
]