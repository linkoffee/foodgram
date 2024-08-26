from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from recipes.models import Recipe
from .models import User, Subscription

admin.site.empty_value_display = 'Здесь пока ничего нет:('


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ панель для пользователя."""

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'recipes_count',
        'subscribers_count',
    )
    list_editable = (
        'first_name',
        'last_name',
    )
    search_fields = (
        'email',
        'username',
    )
    list_filter = (
        'email',
        'username',
    )

    @admin.display(description='Рецепты')
    def recipes_count(self, obj):
        """Считает кол-во рецептов пользователя."""

        return Recipe.objects.filter(author=obj).count()

    @admin.display(description='Подписчики')
    def subscribers_count(self, obj):
        """Считает кол-во подписчиков пользователя."""

        return Subscription.objects.filter(author=obj).count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ панель для подписки."""

    list_display = (
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author',
    )
    list_filter = (
        'user',
        'author',
    )
