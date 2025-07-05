from rest_framework import serializers

from django.core.validators import MinValueValidator
from recipes.models import RecipeIngredient
from ingredients.models import Ingredient


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
