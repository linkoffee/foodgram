## Локальное тестирование проекта:

### Ручное тестирование:
1. Клонировать репозиторий и перейти в него в командной строке:
```console
git clone https://github.com/linkoffee/foodgram.git
```
```console
cd foodgram
```
2. Cоздать и активировать виртуальное окружение:
```console
python3 -m venv venv
```
* Если у вас Linux/macOS

    ```console
    source venv/bin/activate
    ```
* Если у вас windows

    ```console
    source venv/scripts/activate
    ```
```console
python3 -m pip install --upgrade pip
```
3. Установить зависимости из файла requirements.txt:
```console
pip install -r requirements.txt
```
4. Выполнить миграции:
```console
python3 manage.py migrate
```
5. Запустить проект:
```console
python3 manage.py runserver
```

### Запуск контейнеров:
1. Вам нужно находится в корневой директории проекта, где находится файл `docker-compose.yml`:
```
(venv) 
user@user-pc MINGW64 Dev/foodgram (main)
```
2. Запустите контейнеры:
```console
docker-compose up --build
```
После выполнения этой команды начнется сборка nginx, backend и frontend контейнеров.

3. Откройте второй терминал, перейдите в корневую директорию проекта, и последовательно выполните команды миграции, сбора и копирования статики, импорта json:
```console
docker-compose -f docker-compose.yml exec backend python manage.py migrate
```
```console
docker-compose -f docker-compose.yml exec backend python manage.py collectstatic
```
```console
docker-compose -f docker-compose.yml exec backend python manage.py cp -r /app/static/. /static/static/
```
```console
docker-compose -f docker-compose.yml exec backend python manage.py import_data
```
После этого сервис станет доступен для тестирования по адресу http://localhost:8000/ или http://127.0.0.1:8000/

### Ссылки:
[Про тестирование в Postman](https://github.com/linkoffee/foodgram/blob/main/postman_collection/README.md)

[Запуск проекта в продакшен](https://github.com/linkoffee/foodgram/blob/main/README.md#%D0%BA%D0%B0%D0%BA-%D1%80%D0%B0%D0%B7%D0%B2%D0%B5%D1%80%D0%BD%D1%83%D1%82%D1%8C-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82)
