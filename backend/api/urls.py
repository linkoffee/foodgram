from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
)

router_v1 = DefaultRouter()
router_v1.register(
    'users', UserViewSet, basename='users'
)
router_v1.register(
    'recipes', RecipeViewSet, basename='recipes'
)
router_v1.register(
    'ingredients', IngredientViewSet, basename='ingredients'
)
router_v1.register(
    'tags', TagViewSet, basename='tags'
)

urlpatterns = [
    path('', include(router_v1.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
