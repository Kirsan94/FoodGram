from django.urls import path, include
from rest_framework import routers

from .views import TagViewSet, RecipeViewSet, IngredientViewSet, UserViewSet


app_name = "api"

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('users/subscriptions/', UserViewSet.as_view({
        'get': 'subscriptions',
    })),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),

]
