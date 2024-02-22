# image officielle python : python version : 3.12, base sur debian bookworm, slim pour petite image
FROM python:3.12-slim-bookworm

# update and install utilies
RUN apt update -y \
	&& apt upgrade -y
	&& apt install curl git vim

RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"

# ensure python output send straight to term and not buffered
ENV PYTHONUNBUFFERED 1

ENV APP_NAME ${APP_NAME}
ENV HOST ${HOST}
ENV PORT ${PORT}


# create directory for docker volume where app will be
RUN mkdir /app
WORKDIR /app

# install django requirements
COPY requirements_base.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt && rm -f /app/requirements.txt

# setup alias 
RUN echo >> /root/.bashrc \
	alias init="\"django-admin startproject \${APP_NAME} /app && echo django project created! || echo failed to create django project\"\n"\
	alias mig="\"python /app/manage.py migrate\"\n" \
	alias run="\"python /app/manage.py runserver \${HOST}:\${PORT}\"\n" \
	alias conf="\"echo name: \${APP_NAME}, host: \${HOST}:\${PORT}\"\n" \
	alias help="\"echo init: start django project\necho mig: migrate\n echo run: launch django testserver\n echo conf: print app info\necho try to 'type [alias]' for exact command\"\n"

EXPOSE ${PORT}

# no entrypoint because it's dev environnement, use make enter to start container shell
