"""
Скрипт заливки данных из csv в базу
Работает напрямую с моделями
Пример команды:
python manage.py load_scv *названия файлов, без расширения, через пробел*
Осторожно!!! Переписывает записи с существующими ID!!!
При необходимости менять ID записи в scv на свободный
"""


import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from foodgram.models import Ingredient

# Словарь допустимых параметров/названий файла
# Определяет модель, в которую будем заливать данные
# Дополнять по добавлению новых моделей
CHOICES = {
    'ingredients': Ingredient,
}
BASE_DIR = settings.BASE_DIR


class Command(BaseCommand):
    # Считывает аргумены запуска через пробел
    # Аргументами являются названия файлов без расширения ака "users"
    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, **options):
        for file in options['csv_file']:
            model = CHOICES[file]
            csv_file = os.path.join(BASE_DIR, './data/' + file + '.csv')
            datareader = csv.reader(
                open(csv_file, encoding='utf-8'),
                delimiter=',',
                quotechar='"'
            )
            next(datareader)
            try:
                print(file + ':')
                for row in datareader:
                    print('    ', *row)
                    obj = model(*row)
                    obj.save()
            except Exception as e:
                print(e)
