#!/bin/sh
set -e

sleep 10

python -m app.init_db

exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload