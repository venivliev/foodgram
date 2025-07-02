from django.contrib import admin
from django.utils.html import format_html
from .models import Recipe, RecipeIngredient, ShoppingCart, Favorite


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'display_image', 'pub_date')
    list_filter = ('author', 'pub_date')
    search_fields = ('name', 'author__username', 'author__email', 'text')
    readonly_fields = ('pub_date',)
    inlines = (RecipeIngredientInline,)

    fieldsets = (
        (None, {
            'fields': ('author', 'name', 'text', 'cooking_time')
        }),
        ('Медиа', {
            'fields': ('image',)
        }),
        ('Дополнительно', {
            'fields': ('pub_date',)
        }),
    )

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"

    display_image.short_description = 'Изображение'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__username', 'recipe__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__username', 'recipe__name')