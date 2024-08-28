from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField

from recipes.constants import MIN_INGREDIENTS_AMOUNT, MAX_INGREDIENTS_AMOUNT
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientInRecipe,
    ShoppingCart,
    Favorite,
)
from users.models import User, Subscription


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + (
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and request.user.subscriber.filter(author=obj).exists()
        )


class UserAvatarSerializer(UserSerializer):
    """Сериализатор для работы с аватаром пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionReceiveSerializer(UserSerializer):
    """Сериализатор для получения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True,
        default=0
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        """Получить список рецептов."""
        recipes = obj.recipes.all()
        request = self.context.get('request')
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit:
                try:
                    recipes = recipes[:int(recipes_limit)]
                except (ValueError, TypeError):
                    pass

        return RecipeShortSerializer(
            recipes, context=self.context, many=True
        ).data


class SubscribeToSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки или отписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def to_representation(self, instance):
        return SubscriptionReceiveSerializer(
            instance.author, context=self.context
        ).data

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя'
            )
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENTS_AMOUNT,
        max_value=MAX_INGREDIENTS_AMOUNT,
        error_messages={
            'min_value': 'Кол-во ингредиента не может быть меньше '
            f'{MIN_INGREDIENTS_AMOUNT}.',
            'max_value': 'Кол-во ингредиента не может быть больше '
            f'{MAX_INGREDIENTS_AMOUNT}.',
            'invalid': 'Укажите корректное кол-во ингредиента.',
        }
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для получения краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReceiveSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_in_recipe',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.shoppingcarts.filter(user=request.user).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    ingredients = AddIngredientInRecipeSerializer(
        many=True,
        allow_empty=False,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_empty=False,
    )
    image = Base64ImageField(
        allow_null=False,
        allow_empty_file=False,
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        return RecipeReceiveSerializer(instance, context=self.context).data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self.add_ingredient(ingredients=ingredients, recipe=recipe)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])

        instance.ingredients.clear()
        self.add_ingredient(ingredients=ingredients, recipe=instance)
        instance.tags.set(tags)

        return super().update(instance, validated_data)

    @transaction.atomic
    def add_ingredient(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            ],
            ignore_conflicts=True
        )

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        tags = data.get('tags', [])

        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты должны быть уникальными.'
            })

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({
                'tags': 'Теги должны быть уникальными.'
            })

        return data


class ShoppingCartFavoriteSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для избранного и списка покупок."""

    class Meta:
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context=self.context
        ).data

    def validate(self, attrs):
        model = self.Meta.model
        user = attrs['user']
        recipe = attrs['recipe']

        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'non_field_errors': [
                    f'{model._meta.verbose_name} с таким '
                    'пользователем и рецептом уже существует.'
                ]
            })

        return attrs


class ShoppingCartSerializer(ShoppingCartFavoriteSerializer):
    """Сериализатор для списка покупок."""

    class Meta(ShoppingCartFavoriteSerializer.Meta):
        model = ShoppingCart


class FavoriteSerializer(ShoppingCartFavoriteSerializer):
    """Сериализатор для избранного."""

    class Meta(ShoppingCartFavoriteSerializer.Meta):
        model = Favorite
