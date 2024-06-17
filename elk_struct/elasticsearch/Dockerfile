#---- base image ------------------------------------------------------#

FROM    docker.elastic.co/elasticsearch/elasticsearch:8.14.1

#---- configuration files ---------------------------------------------#

RUN     mkdir -p /usr/share/elasticsearch/scripts

COPY    scripts/logs_policy.sh /usr/share/elasticsearch/scripts/
