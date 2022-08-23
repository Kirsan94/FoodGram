from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, HttpResponse
from django.db.models import Sum
from foodgram.models import Subscription
from .permissions import IsAuthorOrAdminOrReadOnly
from .filters import RecipeFilter
from .serializers import (
    Tag,
    TagSerializer,
    Recipe,
    RecipeSerializer,
    Favorite,
    FavoriteSerializer,
    Ingredient,
    IngredientSerializer,
    ShoppingList,
    ShoppingListSerializer,
    RecipeIngredient,
    User,
    UserSubscriptionSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
    filterset_class = RecipeFilter
    filterset_fields = (
        'tags',
        'author',
        'is_favorited',
        'is_in_shopping_cart'
    )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        current_user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = Favorite.objects.filter(
            user=current_user,
            recipe=recipe
        )
        if request.method == 'POST':
            serializer = FavoriteSerializer(recipe)
            if recipe_in_favorite.exists():
                data = {'errors': 'Этот рецепт уже есть в избранном.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=current_user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not recipe_in_favorite.exists():
                data = {
                    'errors': 'Этого рецепта нет в избранном пользователя.'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            recipe_in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        current_user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_shopping_cart = ShoppingList.objects.filter(
            user=current_user, recipe=recipe)
        if request.method == 'POST':
            serializer = ShoppingListSerializer(recipe)
            if in_shopping_cart.exists():
                data = {'errors': 'Этот рецепт уже есть в списке покупок.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            ShoppingList.objects.create(user=current_user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not in_shopping_cart.exists():
                data = {
                    'errors': 'Этого рецепта нет в списке покупок.'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppinglist__user=request.user)
        ingrediants_values = ingredients.values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')
        shopping_cart = '\n'.join([
            f'{ingredient["ingredient__name"]} - {ingredient["amount"]} '
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingrediants_values
        ])
        return HttpResponse(shopping_cart, content_type='application/txt')


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer
    queryset = User.objects.all()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        current_user = self.request.user
        author = get_object_or_404(User, pk=pk)
        in_subscribed = Subscription.objects.filter(
            user=current_user, author=author)
        if request.method == 'POST':
            serializer = UserSubscriptionSerializer(
                author,
                context={'request': request}
            )
            if in_subscribed.exists():
                data = {'errors': 'Вы уже подписаны на этого автора.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            if author == current_user:
                data = {'errors': 'Нельзя подписаться на себя.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(user=current_user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not in_subscribed.exists():
                data = {
                    'errors': 'Вы не подписаны на этого автора.'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            in_subscribed.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        current_user = self.request.user
        user_subscribtions = User.objects.filter(subscribed__user=current_user)
        subscriptions_paginated = self.paginate_queryset(user_subscribtions)
        serializer = UserSubscriptionSerializer(
            subscriptions_paginated,
            many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
