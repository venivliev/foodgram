from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.core.validators import MinValueValidator

from recipes.models import RecipeIngredient, Recipe
from ingredients.models import Ingredient
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
    author = CustomUserSerializer(
        read_only=True
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        source="recipe_ingredients",
    )
    image = Base64ImageField(
        required=True,
        allow_null=False
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients", "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST':
            if 'image' not in self.initial_data or not self.initial_data.get('image'):
                raise serializers.ValidationError(
                    {
                        "image":
                            [
                                "Img is Null"
                            ]
                    }
                )
        elif request.method in ['PATCH', 'PUT']:
            if 'image' in self.initial_data and not self.initial_data.get('image'):
                raise serializers.ValidationError(
                    {"image": ["image is null"]}
                )
            if 'ingredients' not in self.initial_data or not self.initial_data.get('ingredients'):
                raise serializers.ValidationError(
                    {"ingredients": [
                        "image is required"]
                    }
                )

        return data

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                "Ing is Null"
            )
        ingredient_ids = [
            ingredient["ingredient"]["id"] for ingredient in ingredients
        ]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError("Ing is duplicated")
        return ingredients


    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (
                request and
                request.user.is_authenticated and
                obj.favorite.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.shopping_cart.filter(
                user=request.user
            ).exists()
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipe_ingredients", [])
        recipe = super().create(validated_data)
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data["ingredient"]["id"].id,
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        )
        return recipe

    def update(self, instance, validated_data):
        image = validated_data.get("image")
        if image == "":
            raise serializers.ValidationError(
                {"image": "image is null"}
            )
        if "image" not in validated_data:
            validated_data["image"] = instance.image
        ingredients_data = validated_data.pop("recipe_ingredients", [])
        instance = super().update(instance, validated_data)
        instance.recipe_ingredients.all().delete()
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=instance,
                ingredient_id=ingredient_data["ingredient"]["id"].id,
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        )
        return instance
