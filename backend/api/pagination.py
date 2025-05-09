from foodgram_backend.settings import PAGE_SIZE
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Класс кастомной пагинации."""
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
