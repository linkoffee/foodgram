import os
import json

from django.core.management.base import BaseCommand

from recipes.models import Tag, Ingredient

# Путь до директории с json-файлами
JSON_PATH = os.path.join('..', 'data')

# Словарь соответствий модели и json-файла
MODEL_FILE_MATCHING = {
    Tag: 'tags.json',
    Ingredient: 'ingredients.json'
}


class Command(BaseCommand):
    """Пользовательская команда Django для импорта данных из json в БД."""

    help = 'Загружает данные из файлов json в БД'

    def handle(self, *args, **kwargs):
        for model, file_name in MODEL_FILE_MATCHING.items():
            file_path = os.path.join(JSON_PATH, file_name)
            error_occurred = False
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    total_items = len(data)
                    for index, item in enumerate(data, start=1):
                        model.objects.get_or_create(**item)
                        progress_percent = (index / total_items) * 100
                        self.stdout.write(
                            self.style.WARNING(
                                f'Importing {model.__name__} objects... '
                                f'{progress_percent:.2f}% '
                                f'[{index}/{total_items}]'
                            )
                        )
            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing file {file_path}: {error}'
                    )
                )
                error_occurred = True

            if error_occurred:
                self.stdout.write(
                    self.style.ERROR(
                        f'FAILED TO LOAD `{model.__name__.upper()}` DATA'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'SUCCESSFULLY LOADED `{model.__name__.upper()}` DATA'
                    )
                )
