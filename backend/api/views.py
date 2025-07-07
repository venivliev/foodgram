from django.conf import settings
from django.db.models import F
from rest_framework.response import Response
from rest_framework import (
    response,
    status,
    viewsets,
    authtoken
)
from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.storage import default_storage
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from hashids import Hashids

from users.models import Subscription, User
from cart.models import ShoppingCart
from recipes.models import Recipe, Favorite, RecipeIngredient
from ingredients.models import Ingredient
from api.serializers import (
    UserCreateSerializer,
    CustomUserSerializer,
    ReadUserSerializer,
    AvatarSerializer,
    IngredientSerializer,
    AuthTokenSerializer,
    ChangePasswordSerializer,
    SubscribeSerializer,
    SubscribeCreateSerializer
)
from api.recipes_serializers import RecipeSerializer
from api.shorts_serializers import RecipeShortSerializer
from foodgram_config.paginations import UserPagination, RecipePagination
from foodgram_config.filters import IngredientFilter
from foodgram_config.recipes_filters import RecipeFilter
from foodgram_config.permissions import IsAuthorOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserPagination
    http_method_names = [
        'get', 'post', 'put', 'patch', 'delete'
    ]

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe',
    )
    def subscribe(self, request, pk=None):
        author_of_sub = get_object_or_404(User, id=pk)

        if request.user == author_of_sub:
            return Response(
                {'errors': 'sub for myself'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == 'POST':
            if Subscription.objects.filter(
                    user=request.user,
                    subscribed_to=author_of_sub
            ).exists():
                return Response(
                    {'errors': 'sub is already'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Subscription.objects.create(
                user=request.user,
                subscribed_to=author_of_sub
            )
            serializer = SubscribeSerializer(
                author_of_sub,
                context={'request': request}
            )
            serializer_data = serializer.data
            return Response(
                serializer_data,
                status=status.HTTP_201_CREATED
            )
        else:

            subscription = Subscription.objects.filter(
                user=request.user,
                subscribed_to=author_of_sub
            ).first()

            if not subscription:
                return Response(
                    {'errors': 'sub is Null'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscription.delete()

            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        subs_list = User.objects.filter(
            users_subscribers__user=request.user
        )
        page = self.paginate_queryset(subs_list)  # страничка
        serializer = self.get_serializer(
            page,
            many=True
        )
        serializer_data = serializer.data
        return self.get_paginated_response(
            serializer_data
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return ChangePasswordSerializer
        elif self.action == 'subscribe' and self.request.method == 'POST':
            return SubscribeCreateSerializer
        elif self.action in ['avatar', 'retrieve']:
            return CustomUserSerializer
        elif self.action in ['subscribe', 'subscriptions']:
            return SubscribeSerializer
        else:
            return ReadUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )
        if serializer.is_valid():
            user = serializer.save()
            response_data = UserCreateSerializer(
                user
            ).data
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
        serializer.is_valid(
            raise_exception=True
        )
        token, created = authtoken.models.Token.objects.get_or_create(
            user=serializer.validated_data['user']
        )
        return response.Response(
            {'auth_token': token.key}
        )


hashids = Hashids(salt=settings.SECRET_KEY, min_length=6)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]
    pagination_class = RecipePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        recipe = serializer.save(author=self.request.user)
        recipe.short_code = hashids.encode(recipe.id)
        recipe.save()

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def link(self, request, *args, **kwargs):
        recipe = self.get_object()
        base_url = request.build_absolute_uri('/')[:-1]
        total_url = f'{base_url}/r/{recipe.short_code}'
        result = {'short-link': total_url}
        return response.Response(
            result,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        url_name="favorite",
        permission_classes=[
            IsAuthenticated
        ],
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(
            Recipe,
            id=pk
        )
        instance, created = Favorite.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )

        if not created:
            return response.Response(
                {"errors": "Fav is already"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RecipeShortSerializer(
            recipe,
            context={'request': request}
        )
        serializer_data = serializer.data
        return response.Response(
            serializer_data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=["post"],
        url_name="shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        # Вынести в общее, с фаворитом
        recipe = get_object_or_404(
            Recipe,
            id=pk
        )
        instance, created = ShoppingCart.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )

        if not created:
            return response.Response(
                {"errors": f"Рецепт корзине уже есть"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RecipeShortSerializer(
            recipe,
            context={'request': request}
        )
        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def remove_from_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        cou, arg = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        if cou == 0:
            return response.Response(
                {'errors': "fav is null"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        c, *args = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()

        if c == 0:
            return response.Response(
                {'errors': "shop is null"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["GET"],
        url_path="download_shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def export_shopping_list(self, request):
        """Генерирует текстовый файл со списком покупок для авторизованного пользователя."""
        current_time = timezone.now()

        # Получаем рецепты из корзины пользователя
        user_cart_recipes = Recipe.objects.filter(
            shopping_cart__user=request.user
        ).select_related('author').prefetch_related('recipe_ingredients__ingredient')

        # Агрегируем ингредиенты с суммированием количества
        aggregated_ingredients = (
            RecipeIngredient.objects.filter(recipe__in=user_cart_recipes)
            .values(
                ingredient_name=F('ingredient__name'),
                unit=F('ingredient__measurement_unit')
            )
            .annotate(total=Sum('amount'))
            .order_by('ingredient_name')
        )

        # Формируем содержимое файла
        file_content = [
            "=== Мой список покупок ===",
            f"Создан: {current_time.strftime('%d.%m.%Y в %H:%M')}",
            f"Количество рецептов: {user_cart_recipes.count()}",
            f"Всего позиций: {aggregated_ingredients.count()}",
            "",
            "Необходимые ингредиенты:",
        ]

        # Добавляем ингредиенты с нумерацией
        file_content.extend(
            f"{i}. {item['ingredient_name'].title()} — {item['total']} {item['unit']}"
            for i, item in enumerate(aggregated_ingredients, 1)
        )

        # Добавляем список рецептов
        file_content.extend([
            "",
            "Рецепты в списке:",
            *(
                f"• {recipe.name} ({recipe.author.username})"
                for recipe in user_cart_recipes
            )
        ])

        # Создаем файловый ответ
        response = HttpResponse(
            content="\n".join(file_content),
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; '
            f'filename="shopping_list_{current_time.strftime("%Y%m%d_%H%M")}.txt"'
        )

        return response
