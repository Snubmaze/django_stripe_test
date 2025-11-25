#!/bin/bash
set -e

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Creating admin superuser..."
python manage.py create_admin

echo "Initializing data..."
python manage.py initdata

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000