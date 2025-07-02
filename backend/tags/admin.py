from django.contrib import admin
from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')  # Поля, отображаемые в списке
    list_display_links = ('name',)  # Поля-ссылки для перехода к редактированию
    search_fields = ('name', 'slug')  # Поля для поиска
    prepopulated_fields = {'slug': ('name',)}  # Автозаполнение slug на основе name

    fieldsets = (
        (None, {
            'fields': ('name', 'slug')
        }),
    )