#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

PORT=${PORT:-8000}

echo "Environment Vars"
printenv
echo "Django migrate"
python manage.py migrate --noinput
echo "Create scheduled tasks (if needed)"
python manage.py create_scheduled_tasks
echo "Run Gunicorn"
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 zon_prep_ocr_project.wsgi:application
