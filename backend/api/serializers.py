from rest_framework import serializers

from users.models import Subscription, User


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
