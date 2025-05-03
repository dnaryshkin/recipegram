from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Класс кастомной пагинации."""
    page_size = 4
    page_size_query_param = 'limit'