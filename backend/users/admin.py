from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

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

    def save_model(self, request, obj, form, change):
        """Проверка, что пользователь не может подписаться на себя."""

        if obj.user == obj.author:
            self.message_user(
                request,
                'Вы не можете подписаться на самого себя.',
                level=messages.ERROR
            )
        else:
            super().save_model(request, obj, form, change)
