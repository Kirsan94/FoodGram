from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram.models import Subscription

from .filters import RecipeFilter, IngredientFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (Favorite, FavoriteSerializer, Ingredient,
                          IngredientSerializer, Recipe, RecipeIngredient,
                          RecipeSerializer, ShoppingList,
                          ShoppingListSerializer, Tag, TagSerializer, User,
                          UserSubscriptionSerializer)


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для тэгов.
    """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для ингредиентов.
    """
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filterset_class = IngredientFilter
    filterset_fields = (
        'name'
    )


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для рецептов.
    Имеет @action для добавления в избранное и список покупок,
    а также для скачивания списка покупок файлом.
    """
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
        data = {'user': current_user, 'recipe': recipe}
        serializer = FavoriteSerializer(
            data=data,
            context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            Favorite.objects.create(user=current_user, recipe=recipe)
            serializer = FavoriteSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        data = {'user': current_user, 'recipe': recipe}
        serializer = ShoppingListSerializer(
            data=data,
            context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            ShoppingList.objects.create(user=current_user, recipe=recipe)
            serializer = ShoppingListSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
    """
    Вьюсет для пользователей.
    Имеет @action для подписки на автора и просмотра своих подписок.
    """
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
        data = {'user': current_user, 'author': author}
        serializer = UserSubscriptionSerializer(
            data=data,
            context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            Subscription.objects.create(user=current_user, author=author)
            serializer = UserSubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
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
