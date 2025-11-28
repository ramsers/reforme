#!/bin/bash
set -e

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Seeding demo data..."
python manage.py seed_demo_data || echo "Seed skipped (already exists)"

echo "Starting RQ worker in background..."
python manage.py rqworker default &

echo "Starting Gunicorn web server..."
gunicorn reformeApi.wsgi:application --bind 0.0.0.0:$PORT --timeout 120
chmod +x start.sh
