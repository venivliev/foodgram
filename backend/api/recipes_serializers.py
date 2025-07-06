from rest_framework import serializers

from django.core.validators import MinValueValidator
from recipes.models import RecipeIngredient, Recipe
from ingredients.models import Ingredient
from drf_extra_fields.fields import Base64ImageField
from api.serializers import CustomUserSerializer


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient.id"
    )
    name = serializers.CharField(
        source="ingredient.name",
        read_only=True
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source="ingredient.measurement_unit",
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount"
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredients"
    )
    image = Base64ImageField(required=True, allow_null=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    class Meta:
        model = Recipe
        fields = (            "id",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
                              )