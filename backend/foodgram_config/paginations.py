from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = 25
    page_size = 6
