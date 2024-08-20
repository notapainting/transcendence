
FROM    docker.elastic.co/kibana/kibana:8.14.1

RUN     mkdir -p /usr/share/kibana/scripts/JSON

COPY    scripts/data_views.sh /usr/share/kibana/scripts/
COPY    scripts/dashboards.sh /usr/share/kibana/scripts/
COPY    scripts/JSON/dash.json /usr/share/kibana/scripts/JSON
COPY    scripts/JSON/nginx_data_view.json /usr/share/kibana/scripts/JSON
COPY    scripts/JSON/filebeat_data_view.json /usr/share/kibana/scripts/JSON
