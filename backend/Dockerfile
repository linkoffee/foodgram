FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
COPY data/tags.json /app/data/tags.json
COPY data/ingredients.json /app/data/ingredients.json
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]