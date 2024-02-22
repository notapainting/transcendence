FROM nginx

RUN rm /etc/nginx/conf.d/default.conf

COPY ./nginx.conf /etc/nginx/conf.d/

COPY front/index.html /usr/share/nginx/html/

COPY front/assets /usr/share/nginx/html/assets