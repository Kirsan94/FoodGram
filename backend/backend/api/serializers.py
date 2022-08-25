from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from foodgram.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                             ShoppingList, Subscription, Tag)
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from users.models import User
from users.serializers import CustomUserSerializer


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи рецепта с ингредиентом.
    Подтягивает id, name и measurement_unit из связанного ингредиента.
    """
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.IntegerField(
        source='ingredient.id'
    )
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тэгов.
    """
    class Meta:
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """
    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов.
    Подтягивает данные их объекта тэгов, автора и ингредиента.
    Также, отображает наличие рецепта в избранном и списке закупок.
    """
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = CustomUserSerializer(
        read_only=True,
        default=CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient',
        required=True
    )
    image = Base64ImageField(use_url=True, required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        data = super(RecipeSerializer, self).to_representation(instance)
        data['tags'] = TagSerializer(instance.tags.all(), many=True).data
        data['ingredients'] = RecipeIngredientSerializer(
            instance.recipeingredient.all(),
            many=True
        ).data
        return data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def validate_cooking_time(self, value):
        cooking_time = value
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовление должно быть больше нуля!'
            })
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы 1 игредиент'
            )
        ingredient_list = []
        for ingredient_item in value:
            ingredient_id = ingredient_item['ingredient'].get('id')
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_id)
            if ingredient in ingredient_list:
                raise serializers.ValidationError('Ингридиенты должны '
                                                  'быть уникальными')
            ingredient_list.append(ingredient)

            amount = ingredient_item.get('amount')
            if int(amount) <= 0:
                raise serializers.ValidationError('Проверьте, что количество'
                                                  'ингредиента больше нуля')

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError({
                'tags': 'Нужно выбрать хотя бы один тэг!'
            })

        if len(value) == len(set(value)):
            raise serializers.ValidationError({
                'tags': 'Тэги должны быть уникальными!'
            })

    def ingredients_creation(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients_data = self.initial_data.pop('ingredients')
        tags_data = self.initial_data.pop('tags')
        validated_data.pop('recipeingredient')
        validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.ingredients_creation(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        ingredients = validated_data.pop('ingredients')
        validated_data.pop('recipeingredient')
        self.ingredients_creation(ingredients, instance)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для избранных рецептов.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)

    def validate(self, data):
        request = self.context.get('request')
        current_user = request.user
        recipe_in_favorite = Favorite.objects.filter(
            user=current_user,
            recipe=self.initial_data['recipe']
        )
        if request.method == 'POST':
            if recipe_in_favorite.exists():
                raise serializers.ValidationError({
                    'errors': 'Этот рецепт уже есть в избранном.'
                })
        if request.method == 'DELETE':
            if not recipe_in_favorite.exists():
                raise serializers.ValidationError({
                    'errors': 'Этого рецепта нет в избранном пользователя.'
                })
        return data


class ShoppingListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка покупок.
    """
    image = Base64ImageField(use_url=True, required=True)
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.StringRelatedField()
    cooking_time = serializers.IntegerField()

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        model = ShoppingList

    def validate(self, data):
        request = self.context.get('request')
        current_user = request.user
        recipe_in_shopping_list = ShoppingList.objects.filter(
            user=current_user,
            recipe=self.initial_data['recipe']
        )
        if request.method == 'POST':
            if recipe_in_shopping_list.exists():
                raise serializers.ValidationError({
                    'errors': 'Этот рецепт уже есть в списке покупок.'
                })
        if request.method == 'DELETE':
            if not recipe_in_shopping_list.exists():
                raise serializers.ValidationError({
                    'errors':
                    'Этого рецепта нет в списке покупок пользователя.'
                })
        return data


class UserSubscriptionSerializer(CustomUserSerializer):
    """
    Сериализатор для подписок.
    Подтягивает список рецептов авторов
    на которых подписан пользователь.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes
        if limit:
            recipes = recipes.all()[:int(limit)]
        context = {'request': request}
        return ShoppingListSerializer(recipes, context=context, many=True).data

    def validate(self, data):
        request = self.context.get('request')
        current_user = request.user
        author = self.initial_data['author']
        in_subscribed = Subscription.objects.filter(
            user=current_user,
            author=author
        )
        if request.method == 'POST':
            if in_subscribed.exists():
                raise serializers.ValidationError({
                    'errors': 'Вы уже подписаны на этого автора.'
                })
            if author == current_user:
                raise serializers.ValidationError({
                    'errors': 'Нельзя подписаться на себя.'
                })
        if request.method == 'DELETE':
            if not in_subscribed.exists():
                raise serializers.ValidationError({
                    'errors': 'Вы не подписаны на этого автора.'
                })
        return data
