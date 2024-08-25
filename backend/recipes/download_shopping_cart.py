from datetime import date
import tempfile

from django.http import FileResponse
from dotenv import load_dotenv

load_dotenv()


def download_txt(data, user):
    """Функция для загрузки списка покупок в txt формате."""

    file_name = f'{user}`s_shopping_cart.txt'
    current_date = date.today().strftime('%d-%m-%Y')

    header = f'Список покупок {user}\nДата: {current_date}'
    file_data = '\n'.join([
        f'{item["ingredient__name"]} {item["total_amount"]} '
        f'{item["ingredient__measurement_unit"]}'
        for item in data
    ])

    content = f'{header}\n\n{file_data}'

    with tempfile.NamedTemporaryFile(
        delete=False,
        mode='w',
        encoding='utf-8',
    ) as temp_file:
        temp_file.write(content)
        temp_file_name = temp_file.name

    response = FileResponse(
        open(temp_file_name, 'rb'),
        content_type='text/plain; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response
