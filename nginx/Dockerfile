FROM nginx:1.18.0

# copy nginx's configuration file and self signed certificate for https
COPY ./conf/nginx-selfsigned.crt /etc/nginx/ssl/nginx-selfsigned.crt
COPY ./conf/nginx-selfsigned.key /etc/nginx/ssl/nginx-selfsigned..key

COPY ./conf/nginx.conf /etc/nginx/conf.d/nginx.conf

# create directory for your website
# RUN mkdir /var/www/trmdr.com/

# copy our website
# COPY ./front/* /var/www/trmdr.com