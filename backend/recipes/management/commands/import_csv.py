import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient


class Command(BaseCommand):
    """Класс для импорта данных из CSV файлов."""
    help = 'Импортирует файлы csv с данными'

    @transaction.atomic
    def handle(self, *args, **options):
        dir_place = settings.BASE_DIR / 'data'
        try:
            self.import_ingredient(dir_place)
            self.stdout.write(self.style.SUCCESS(
                'Импорт всех данный успешно завершен!'
            ))
        except Exception:
            self.stdout.write(self.style.ERROR('Импорт данных не выполнен!'))

    def import_ingredient(self, dir_place):
        with open(dir_place / 'ingredients.csv', newline='') as file:
            reader = csv.DictReader(file, delimiter=',')
            Ingredient.objects.all().delete()
            self.stdout.write('Начало импорта данных Ingredients')
            for row in reader:
                try:
                    Ingredient.objects.create(
                        id=int(row['id']),
                        name=row['name'],
                        measurement_unit=row['measurement_unit'],
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка импорта  Ingredient: {e}')
                    )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Импорт данный Ingredients завершен')
                )