#---- base image ------------------------------------------------------#

FROM    docker.elastic.co/kibana/kibana:8.14.1

#---- configuration files ---------------------------------------------#

RUN     mkdir -p /usr/share/kibana/scripts

COPY    scripts/data_views.sh /usr/share/kibana/scripts/
COPY    scripts/dashboards.sh /usr/share/kibana/scripts/
