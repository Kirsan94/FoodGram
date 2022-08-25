from django_filters import rest_framework as filters
from foodgram.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='get_is_in_shopping_cart'
    )

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(favorite__user=self.request.user)
        else:
            return queryset.exclude(favorite__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(
                shoppinglist__user=self.request.user
            )
        else:
            return queryset.exclude(
                shoppinglist__user=self.request.user
            )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name', ]
