from recipes.models import Recipe

from rest_framework.serializers import ModelSerializer


class RecipeShortSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time"
        )
        read_only_fields = fields
