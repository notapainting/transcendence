# image officielle python : python version : 3.12, base sur debian bookworm, slim pour petite image
FROM python:3.12-slim-bookworm

# ensure python output send straight to term and not buffered
ENV PYTHONUNBUFFERED 1

RUN mkdir /code

COPY requirements.txt /code/requirements.txt

WORKDIR /code

# pip freeze > requirements.txt
RUN pip install -r requirements.txt
RUN django-admin startproject app .


EXPOSE 8000

ENTRYPOINT ["bash"]

# first launch contenair
# pip install what needed
# pip freeze > requirements.txt
# python startproject app 
