from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import authenticate

from api.shorts_serializers import RecipeShortSerializer

from users.models import Subscription, User
from ingredients.models import Ingredient


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=True)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True
    )

    def create(self, validated_data):
        data = dict(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            avatar=validated_data.get('avatar'),
            password=validated_data['password']
        )
        user = User.objects.create_user(**data)
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'id',
            'username',
            'first_name',
            'last_name',
        )
        extra_kwargs = {
            'avatar': {'required': False},
        }


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.users_subscriptions.filter(
                subscribed_to=obj
            ).exists()
        return False

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )


class ReadUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = (
            'email',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.users_subscriptions.filter(
                subscribed_to=obj
            ).exists()
        return False


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password,
            )
            if not user:
                msg = 'wrong data'
                raise serializers.ValidationError(
                    msg,
                    code='authorization'
                )
        else:
            msg = 'email, password is required'
            raise serializers.ValidationError(
                msg,
                code='authorization'
            )
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True
    )
    current_password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):
        if not self.context['request'].user.check_password(
                data['current_password']
        ):
            raise serializers.ValidationError(
                {'current_password': 'old_password wrong'}
            )
        if data['current_password'] == data['new_password']:
            raise serializers.ValidationError(
                {'new_password': 'old = new'}
            )
        return data

    def save(self):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source='recipes.count'
    )
    avatar = Base64ImageField(
        required=False
    )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.users_subscriptions.filter(
                subscribed_to=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')

        limit = request.GET.get('recipes_limit')

        recipes = obj.recipes.all()
        new_recipes = recipes
        if limit:
            try:
                limit = int(limit)
                if limit > 0:
                    new_recipes = recipes[:limit]
            except Exception:
                pass

        serializer = RecipeShortSerializer(new_recipes, many=True, read_only=True)
        serializer_data = serializer.data
        return serializer_data

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name'
        )


class SubscribeCreateSerializer(serializers.ModelSerializer):
    def validate(self, data):
        user = data['user']
        author = data['subscribed_to']
        if user == author:
            raise serializers.ValidationError(
                'Sub is yourself'
            )
        if Subscription.objects.filter(
                user=user,
                subscribed_to=author
        ).exists():
            raise serializers.ValidationError(
                'Sub is already'
            )
        return data

    def validate_for_delete(self, user, author):
        if not Subscription.objects.filter(
                user=user,
                subscribed_to=author
        ).exists():
            raise serializers.ValidationError(
                'Sub is null'
            )

    class Meta:
        model = Subscription
        fields = (
            'user',
            'subscribed_to'
        )
