#!/bin/bash

# Ожидание PostgreSQL
until nc -z db 5432; do
    echo "Waiting for PostgreSQL..."
    sleep 0.5
done
echo "Connected to PostgreSQL"

# Выполнение миграций
python manage.py migrate || { echo "Migration failed"; exit 1; }

# Запуск Gunicorn
exec gunicorn --workers 2 --bind 0.0.0.0:8000 --timeout 90 --log-level info foodgram.wsgi
