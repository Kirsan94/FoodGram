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

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
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

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
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
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
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

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
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
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
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
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            ),
        ]
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ['recipe']

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} - {self.amount}'
