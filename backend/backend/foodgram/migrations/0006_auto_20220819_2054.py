# Generated by Django 2.2.16 on 2022-08-19 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0005_auto_20220819_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(blank=True, db_index=True, related_name='recipes', to='foodgram.Tag', verbose_name='Список id тегов'),
        ),
    ]
