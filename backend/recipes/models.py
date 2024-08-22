from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator

from users.models import User
from .constants import (
    MAX_RECIPE_NAME_LEN,
    MAX_TAG_NAME_LEN,
    MAX_TAG_SLUG_LEN,
    MAX_INGREDIENT_NAME_LEN,
    MAX_INGREDIENT_MU_LEN,
    CHAR_LIMIT,
    MIN_INGREDIENTS_AMOUNT,
    MIN_COOKING_TIME,
)


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        unique=True,
        max_length=MAX_INGREDIENT_NAME_LEN,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=MAX_INGREDIENT_MU_LEN,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:CHAR_LIMIT]


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        unique=True,
        max_length=MAX_TAG_NAME_LEN,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_TAG_SLUG_LEN,
        verbose_name='Слаг',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:CHAR_LIMIT]


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=MAX_RECIPE_NAME_LEN,
        verbose_name='Название',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        validators=[
            FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))
        ],
        verbose_name='Картинка',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        db_index=True,
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=(
                    'Время приготовления не может быть меньше '
                    f'{MIN_COOKING_TIME} минут(ы)!'
                )
            )
        ],
        db_index=True,
        verbose_name='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:CHAR_LIMIT]


class IngredientInRecipe(models.Model):
    """Модель ингредиента в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_INGREDIENTS_AMOUNT,
                message=(
                    'Кол-во ингредиентов не может быть '
                    f'меньше {MIN_INGREDIENTS_AMOUNT}!'
                )
            )
        ],
        verbose_name='Кол-во',
    )

    class Meta:
        ordering = ('ingredient',)
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return (
            f'{self.recipe.name} {self.ingredient.name}'
        )


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('user__username',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_shopping_cart',
            )
        ),
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return (
            f'{self.user.username} добавил {self.recipe.name} в список покупок'
        )


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_favorite',
            )
        ),
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return (
            f'{self.user.username} добавил {self.recipe.name} в избранное'
        )
