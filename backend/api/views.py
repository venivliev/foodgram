from django.conf import settings

from rest_framework import (
    response,
    status,
    viewsets,
)
from users.models import Subscription, User
from api.serializers import (
    UserCreateSerializer,
)
from api.paginations import UserPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserPagination
    serializer_class = UserCreateSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = UserCreateSerializer(user).data
            return response.Response(
                response_data, status=status.HTTP_201_CREATED
            )
        return response.Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
