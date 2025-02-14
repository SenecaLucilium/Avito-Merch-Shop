#!/bin/sh
set -e

sleep 10

# Инициализация базы данных
python -m app.init_db

# Запуск сервера
exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload