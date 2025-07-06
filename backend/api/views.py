from django.conf import settings

from rest_framework import (
    response,
    status,
    viewsets,
authtoken
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.core.files.storage import default_storage
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from users.models import Subscription, User
from recipes.models import Recipe
from api.serializers import (
    UserCreateSerializer,
    CustomUserSerializer,
    ReadUserSerializer,
    AvatarSerializer,
    IngredientSerializer,
    AuthTokenSerializer,
    ChangePasswordSerializer
)
from api.recipes_serializers import RecipeSerializer
from rest_framework.views import APIView
from ingredients.models import Ingredient
from foodgram_config.paginations import UserPagination, RecipePagination
from foodgram_config.filters import IngredientFilter
from foodgram_config.permissions import IsAuthorOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserPagination
    http_method_names = [
        'get', 'post', 'put', 'patch', 'delete'
    ]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return ChangePasswordSerializer
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
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='set_password',
        methods=['post'],
    )
    def set_password(self, request):
        """смена пароля"""
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
            request.user.avatar = ""
            request.user.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter
    filter_backends = [DjangoFilterBackend]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ObtainAuthToken(APIView):
    serializer_class = AuthTokenSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = authtoken.models.Token.objects.get_or_create(
            user=user
        )
        return response.Response({'auth_token': token.key})


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]
    pagination_class = RecipePagination