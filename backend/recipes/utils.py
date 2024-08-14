from django.http import HttpResponse
from datetime import date


def download_shopping_cart(data, user):
    """Функция для загрузки списка покупок в txt формате."""

    file_name = f'{user}`s_shopping_cart.txt'
    current_date = date.today().strftime('%d-%m-%Y')
    ingredients = {}

    for recipe in data:
        for ingredient in recipe:
            name = ingredient.ingredient.name
            if name not in ingredients:
                ingredients[name] = {
                    'amount': ingredient.amount,
                    'measurement_unit': ingredient.ingredient.measurement_unit
                }
            else:
                ingredients[name]['amount'] += ingredient.amount

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
