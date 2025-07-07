from django.contrib import admin

from ingredients.models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')  # Отображаемые поля в списке
    list_display_links = ('name',)  # Поля-ссылки для редактирования
    search_fields = ('name',)  # Поля для поиска
    list_filter = ('measurement_unit',)  # Фильтрация по единицам измерения
    ordering = ('name',)  # Сортировка по названию (как в Meta модели)

    fieldsets = (
        (None, {
            'fields': ('name', 'measurement_unit')
        }),
    )
