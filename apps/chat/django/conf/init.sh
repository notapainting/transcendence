#!/bin/bash
python /app/manage.py migrate
gunicorn -c /conf/gunicorn.conf.py auth_service.wsgi:application
