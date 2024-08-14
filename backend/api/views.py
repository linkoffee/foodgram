from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    ShoppingCart,
    Favorite,
)
from users.models import User, Subscription
from .permissions import IsAdminOrAuthor


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = ...
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ...


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение тегов."""

    queryset = Tag.objects.all()
    serializer_class = ...
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Все операции с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthor,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ...
    http_method_names = ('get', 'post', 'patch', 'delete')