from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from djoser.serializers import SetPasswordSerializer
from rest_framework import filters, viewsets, views, permissions, status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientInRecipe,
    ShoppingCart,
    Favorite,
)
from recipes.utils import download_txt, generate_link
from users.models import User, Subscription
from .permissions import IsAdminOrAuthor
from .pagination import LimitPagination
from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    SubscriptionReceiveSerializer,
    SubscribeToSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeCreateSerializer,
    RecipeReceiveSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    UserAvatarSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для юзера."""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]

    @action(
        methods=('GET',),
        permission_classes=(IsAuthenticated,),
        detail=False
    )
    def me(self, request):
        """Возвращает информацию о профиле текущего пользователя."""

        serializer = UserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('POST',),
        permission_classes=(IsAuthenticated,),
        detail=False
    )
    def set_password(self, request):
        """Меняет пароль текущего пользователя по запросу."""

        user = self.request.user

        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('PUT', 'DELETE'),
        url_path='me/avatar',
        detail=False
    )
    def avatar(self, request):
        """Устанавливает, обновляет, либо удаляет аватар пользователя."""

        user = self.request.user

        if request.method == 'DELETE' and user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.method == 'PUT' and request.data:
            serializer = UserAvatarSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(ListAPIView):
    """Вьюсет для просмотра подписок."""

    serializer_class = SubscriptionReceiveSerializer
    pagination_class = LimitPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(subscribed_to__user=self.request.user)


class SubscribeToViewSet(views.APIView):
    """Вьюсет для подписки или отписки от пользователя."""

    pagination_class = LimitPagination
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        user = self.request.user
        data = {'author': author.id, 'user': user.id}
        serializer = SubscribeToSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        user = request.user
        try:
            subscription = Subscription.objects.get(user=user, author=author)
        except Subscription.DoesNotExist:
            return Response(
                {'errors': 'Подписка не найдена.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthor, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return RecipeCreateSerializer
        return RecipeReceiveSerializer

    @action(
        methods=('GET',),
        detail=True,
        url_path='get-link',
    )
    def get_short_link(self, request, pk):
        """Генерация короткой ссылки на рецепт."""

        recipe = self.get_object()
        short_link = generate_link(recipe)

        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,),
        detail=True
    )
    def shopping_cart(self, request, pk):
        """Добавление или удаление из списка покупок, исходя из запроса."""

        if request.method == 'POST':
            return self.add_recipe(request, pk, ShoppingCartSerializer)
        return self.delete_recipe(request, pk, ShoppingCart)

    @action(
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,),
        detail=True,
    )
    def favorite(self, request, pk):
        """Добавление или удаление из избранного, исходя из запроса."""

        if request.method == 'POST':
            return self.add_recipe(request, pk, FavoriteSerializer)
        return self.delete_recipe(request, pk, Favorite)

    @action(
        methods=('GET',),
        permission_classes=(IsAuthenticated,),
        detail=False
    )
    def download_shopping_cart(self, request):
        """Загрузка списка покупок файлом."""

        recipes = Recipe.objects.filter(shopping_carts__user=request.user)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))

        return download_txt(ingredients, user=request.user.username)

    def add_recipe(self, request, pk, serializer_class):
        """Добавление рецепта в избранное или в список покупок."""

        recipe = get_object_or_404(Recipe, pk=pk)

        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = serializer_class(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, request, pk, model):
        """Удаление рецепта из избранного или списка покупок."""

        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        try:
            obj = model.objects.get(recipe_id=recipe.id, user=user)
        except model.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не найден в списке.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
