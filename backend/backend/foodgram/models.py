from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=256, unique=True)
    slug = models.SlugField('Уникальный слаг', unique=True)
    color = models.CharField(
        'Цвет в HEX',
        max_length=256,
        unique=True,
        default='#ffffff'
    )

    def str(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    def str(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=256,
        db_index=True,
        unique=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список id тегов',
        related_name='recipes',
        blank=True,
        db_index=True
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        null=True,
        blank=True,
    )
    text = models.TextField('Описание')
    cooking_time = models.SmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(1, 'Минимальное время приготовления - 1 минута!')
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов',
        through='recipeingredient',
        db_index=True
    )

    class Meta:
        ordering = ['name']

    def str(self):
        return self.name


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppinglist'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='shoppinglist'
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_follow'
            )
        ]


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Название рецепта',
        related_name='recipeingredient',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Название ингредиента',
        related_name='recipeingredient',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    amount = models.SmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(1, 'Невозможны неположительные значения!')
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            ),
        ]
        ordering = ['recipe']
