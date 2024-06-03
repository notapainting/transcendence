# !/bin/bash
python /app/manage.py migrate
gunicorn -c /conf/gunicorn.conf.py user_managment.wsgi:application