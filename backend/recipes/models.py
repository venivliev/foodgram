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
    ingredients = models.ManyToManyField(
        'ingredients.Ingredient',
        through='RecipeIngredient',
        verbose_name='ингридиенты',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )
    short_code = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Код короткой ссылки",
        help_text="Уникальный код для короткой ссылки на рецепт",
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
        related_name='recipe_ingredients',
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
