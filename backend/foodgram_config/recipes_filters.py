from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_in_cart'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_favorited'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_in_shopping_cart',
            'is_favorited'
        )

    def filter_favorited(self, queryset, name, value):
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(favorite__user=self.request.user)
            return queryset.none()
        return queryset

    def filter_in_cart(self, queryset, name, value):
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(shopping_cart__user=self.request.user)
            return queryset.none()
        return queryset
