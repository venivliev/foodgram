from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import authenticate

from users.models import Subscription, User
from ingredients.models import Ingredient

class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=True)


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Создание пользователя
    """
    password = serializers.CharField(write_only=True)

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
                msg = 'Неверные учетные данные.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Обязательные поля: "Email" и "Пароль"'
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs