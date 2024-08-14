from django.contrib import admin

from .models import User, Subscription

admin.site.empty_value_display = 'Здесь пока ничего нет:('


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админ панель для пользователя."""

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
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
