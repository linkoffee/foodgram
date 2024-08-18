import base64
import os
from django.http import HttpResponse
from datetime import date

from dotenv import load_dotenv

load_dotenv()


def download_txt(data, user):
    """Функция для загрузки списка покупок в txt формате."""

    file_name = f'{user}`s_shopping_cart.txt'
    current_date = date.today().strftime('%d-%m-%Y')
    ingredients = {}

    for item in data:
        name = item['ingredient__name']
        amount = item['total_amount']
        measurement_unit = item['ingredient__measurement_unit']

        if name not in ingredients:
            ingredients[name] = {
                'amount': amount,
                'measurement_unit': measurement_unit
            }
        else:
            ingredients[name]['amount'] += amount

    header = f'Список покупок {user}\nДата: {current_date}'
    file_data = [
        f'{name} {info["amount"]} {info["measurement_unit"]}'
        for name, info in ingredients.items()
    ]

    content = '\n'.join([header] + file_data)
    content_type = 'text/plain; charset=utf-8'
    response = HttpResponse(content=content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response


def generate_link(recipe):
    """Функция для генерации уникальной короткой ссылки на рецепт."""

    recipe_id_str = str(recipe.id).encode('utf-8')
    code = base64.urlsafe_b64encode(recipe_id_str).decode('utf-8').rstrip('=')
    short_link = f'{os.getenv("SITE_URL")}/s/{code}'

    return short_link
