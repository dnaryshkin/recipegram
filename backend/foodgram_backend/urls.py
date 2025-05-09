import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path(
        'api/redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    re_path(
        r'^api/openapi-schema\.yml$',
        serve,
        kwargs={
            'path': 'openapi-schema.yml',
            'document_root': os.path.join(settings.BASE_DIR, 'docs')
        }
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
