from django.contrib.auth.models import AbstractUser
from django.db import models

USER = 'user'
ADMIN = 'admin'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
]


class User(AbstractUser):
    """
    Новая модель пользователя, унаследованная от AbstractUser. В модели
    присутствуют новые поля, расширяющие исходную Django-модель:
        is_user - пользователь с базовыми правами (bool);
        is_admin - пользователь, наделенный абсолютными правами (bool).
    """
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        verbose_name='Почта',
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        verbose_name='Статус',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True
    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
