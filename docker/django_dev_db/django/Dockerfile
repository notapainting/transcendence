# image officielle python : python version : 3.12, base sur debian bookworm, slim pour petite image
FROM python:3.12-slim-bookworm

# update and install utilies
RUN apt update -y && apt upgrade -y curl git vim
RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"

# ensure python output send straight to term and not buffered
ENV PYTHONUNBUFFERED 1

# create directory for docker volume where app will be
RUN mkdir /app
WORKDIR /app

# install django requirements
COPY requirements_base.txt /code/requirements.txt
RUN pip install -r requirements.txt


EXPOSE 8000

# no entrypoint because it's dev environnement, use make enter to start container shell
# ENTRYPOINT ["bash"]

# first launch container
# pip install what needed
# pip freeze > requirements.txt
# django-admin startproject app .
# python manage.py migrate
# python manage.py runserver 0.0.0.0:8000

