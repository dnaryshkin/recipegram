from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.views import short_url

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    # Маршруты приложения api
    path('api/', include('api.urls')),
    # Короткая ссылка для рецептов
    path('s/<int:pk>/', short_url, name='short-link'),

]

# Обслуживание статических и медиафайлов в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)