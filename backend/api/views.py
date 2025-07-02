from django.conf import settings

from rest_framework import (
    response,
    status,
    viewsets,
)
from rest_framework.decorators import action
from django.core.files.storage import default_storage
from rest_framework.permissions import IsAuthenticated
from users.models import Subscription, User
from api.serializers import (
    UserCreateSerializer,
    CustomUserSerializer,
    ReadUserSerializer,
    AvatarSerializer,
)
from api.paginations import UserPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserPagination
    http_method_names = [
        'get', 'post', 'put', 'patch', 'delete'
    ]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['avatar', 'retrieve']:
            return CustomUserSerializer
        return ReadUserSerializer

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

    @action(
        methods=['get'],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = CustomUserSerializer(
            request.user,
            context={'request': request}
        )
        return response.Response(
            serializer.data
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='set_password',
        methods=['post'],
    )
    def set_password(self, request):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                status=status.HTTP_204_NO_CONTENT
            )
        return response.Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        methods=['put', 'delete'],
    )
    def avatar(self, request):
        """для аватара"""
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            if serializer.is_valid():
                avatar = serializer.validated_data['avatar']
                request.user.avatar = avatar
                request.user.save()
                return response.Response(
                    {'avatar': request.user.avatar.url},
                    status=status.HTTP_200_OK
                )
            return response.Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.avatar:
            try:
                name = request.user.avatar.name
                if default_storage.exists(name):
                    default_storage.delete(name)
            except Exception:
                pass
            request.user.avatar = None
            request.user.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)