#!/bin/bash
python /app/manage.py migrate

# development server
python /app/manage.py runserver 0.0.0.0:8000
# for daphne
# daphne -b 0.0.0.0 -p 8000 game_back.asgi:application

