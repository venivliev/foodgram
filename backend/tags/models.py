from django.db import models


class Tag(models.Model):
    name = models.CharField(
        max_length=32, verbose_name='азвание тега'
    )
    slug = models.SlugField(
        max_length=32, unique=True, verbose_name='Ключ тега'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name']

    def __str__(self):
        return self.name
