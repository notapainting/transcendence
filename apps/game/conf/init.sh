#!/bin/bash
python /app/manage.py migrate
python /app/manage.py runserver 0.0.0.0:8000
# daphne -b 0.0.0.0 -p 8000 project.asgi:application
