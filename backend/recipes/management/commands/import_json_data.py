import os
import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

# Путь до директории с json-файлом
JSON_PATH = os.path.join('..', 'data', 'ingredients.json')


class Command(BaseCommand):
    help = 'Загружает данные об ингредиентах из файла json в БД'

    def handle(self, *args, **kwargs):
        error_occurred = False
        try:
            with open(JSON_PATH, 'r', encoding='utf-8') as file:
                ingredients = json.load(file)
                total_items = len(ingredients)
                for index, item in enumerate(ingredients, start=1):
                    Ingredient.objects.get_or_create(
                        name=item['name'],
                        measurement_unit=item['measurement_unit'],
                    )
                    progress_percent = (index / total_items) * 100
                    self.stdout.write(
                        self.style.WARNING(
                            f'Processing... {progress_percent:.2f}% '
                            f'[{index}/{total_items}]'
                        )
                    )
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(f'Error processing file {JSON_PATH}: {error}')
            )
            error_occurred = True

        if error_occurred:
            self.stdout.write(
                self.style.ERROR('FAILED TO LOAD DATA')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('SUCCESSFULLY LOADED DATA')
            )
