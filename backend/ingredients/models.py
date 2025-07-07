from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=100, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name
