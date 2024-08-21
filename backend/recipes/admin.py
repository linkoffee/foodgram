from pyexpat.errors import messages
from django.contrib import admin
from django.forms import ValidationError

from .models import Ingredient, Tag, Recipe, ShoppingCart, Favorite

admin.site.empty_value_display = 'Здесь пока ничего нет:('


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ панель для ингредиентов."""

    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ панель для тегов."""

    list_display = (
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )
    list_filter = (
        'name',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """"Админ панель для рецептов."""

    list_display = (
        'author',
        'name',
        'favorite_additions'
    )
    list_editable = (
        'name',
    )
    search_fields = (
        'author',
        'name',
    )
    list_filter = (
        'tags',
    )

    @admin.display(description='Добавлений в избранное')
    def favorite_additions(self, obj):
        """Считает кол-во добавлений рецепта в избранное."""

        return obj.favorites.all().count()

    def save_model(self, request, obj, form, change):
        """Проверка наличия ингредиентов перед сохранением рецепта."""

        try:
            obj.clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, e.message, level=messages.ERROR)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """"Админ панель для рецептов."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
    )
    list_filter = (
        'user',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ панель для избранного."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
    )
    list_filter = (
        'user',
    )
