from django.core.validators import MinValueValidator
from django.db import models

from users.models import User
from ingredients.models import Ingredient


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='название',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='изображение'
    )
    text = models.TextField(
        verbose_name='описание'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name='время готовки',
    )
    tags = models.ManyToManyField(
        'tags.Tag',
        related_name='recipes',
        verbose_name='теги'
    )
    ingredients = models.ManyToManyField(
        'ingredients.Ingredient',
        through='RecipeIngredient',
        verbose_name='ингридиенты',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингридиент',
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name='количество ингридиентов',
    )

    class Meta:
        verbose_name = 'ингридиенты рецепта'
        verbose_name_plural = 'ингридиенты рецептов'

    def __str__(self):
        return f'{self.recipe.name} {self.ingredient.name} {self.amount}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='рецепты',
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'избранные рецепты'

    def __str__(self):
        return f'{self.user} {self.recipe}'
