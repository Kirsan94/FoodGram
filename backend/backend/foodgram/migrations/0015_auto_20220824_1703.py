# Generated by Django 2.2.16 on 2022-08-24 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0014_auto_20220823_2112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(verbose_name='Время приготовления (в минутах)'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveIntegerField(verbose_name='Количество'),
        ),
    ]
