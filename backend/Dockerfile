FROM python:3.11-slim

# Установка зависимостей для psycopg2 и netcat
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libpq-dev gcc netcat-traditional && \
    apt-get clean && \
    apt-get purge -y --auto-remove gcc libpq-dev

# Создание рабочей директории
WORKDIR /app

# Установка Python-зависимостей
COPY requirements.txt ./
RUN pip install -U pip && \
    pip install -r requirements.txt --no-cache-dir

# Копирование проекта
COPY . .

# Сбор статики
RUN python manage.py collectstatic --noinput

# Подготовка скрипта
RUN chmod +x run_app.sh

# Точка входа
ENTRYPOINT ["/app/run_app.sh"]
