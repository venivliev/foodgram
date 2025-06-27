from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name='почта'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='логин',
        validators=[RegexValidator(r'^[\w.@+-]+$')],
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='фамилия'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='аватарка',
    )
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f"Пользователь: {self.username}"
