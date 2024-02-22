FROM nginx:1.18.0

# update and install utilies
RUN apt update -y && apt upgrade -y
RUN apt install -y vim curl git

RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"

RUN mkdir -p /certs /var/www/static/ /logs

COPY ./conf/default.conf /etc/nginx/conf.d/default.conf

