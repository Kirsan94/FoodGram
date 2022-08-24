from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """
    Модель для тэгов рецептов.
    Предполагаемые тэги: Завтрак, Обед, Ужин.
    Допустимо прикрепление нескольких тэгов к рецепту.
    """
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
    """
    Модель для ингредиентов.
    Недопустимы повторения пар Название<->Единица измерения.
    """
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='ingredient_measurement_unit'
            )
        ]

    def str(self):
        return self.name


class Recipe(models.Model):
    """
    Модель для рецептов.
    """
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
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)'
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
    """
    Модель для списка закупок.
    Привязывает рецепт к пользователю в отдельной таблице
    для дальнейшей выгрузки ингредиентов всех рецептов в списке в файл.
    """
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

    def str(self):
        return f'{self.user} - {self.recipe}'


class Favorite(models.Model):
    """
    Модель для избранных рецептов.
    Отражает связь рецепта с пользователем.
    """
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

    def str(self):
        return f'{self.user} - {self.recipe}'


class Subscription(models.Model):
    """
    Модель для подписок на авторов рецептов.
    Отражает связь автора рецептов с пользователем.
    """
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

    def str(self):
        return f'{self.user} - {self.author}'


class RecipeIngredient(models.Model):
    """
    Модель для связи между рецептом и игридиентом.
    Недопустимы повторения пар Рецепт<->Ингредиент
    """
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Название рецепта',
        related_name='recipeingredient',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Название ингредиента',
        related_name='recipeingredient',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        'Количество'
    )

    def str(self):
        return f'{self.recipe} - {self.ingredient} - {self.amount}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            ),
        ]
        ordering = ['recipe']
