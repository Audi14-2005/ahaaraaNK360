#!/usr/bin/env bash
# Start script for Render deployment

# Exit on any error
set -o errexit

# Run database migrations (in case they weren't run during build)
python manage.py migrate

# Start the application
exec python -m gunicorn myproject.wsgi:application --bind 0.0.0.0:$PORT
