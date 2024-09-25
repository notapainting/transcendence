# !/bin/bash
python /app/manage.py migrate
gunicorn --bind 0.0.0.0:8000 user.wsgi:application