from django.contrib import admin

from foodgram.models import (
    Tag,
    Ingredient,
    Recipe,
    ShoppingList,
    Favorite,
    Subscription,
    RecipeIngredient
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('count_favorites',)

    def count_favorites(self, obj):
        return obj.favorite.count()


admin.site.register(Tag)
admin.site.register(ShoppingList)
admin.site.register(Favorite)
admin.site.register(Subscription)
admin.site.register(RecipeIngredient)
