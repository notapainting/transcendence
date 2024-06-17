FROM    docker.elastic.co/beats/filebeat:8.14.1

COPY    --chown=root:filebeat conf/filebeat.yml /usr/share/filebeat/filebeat.yml
COPY    --chown=root:filebeat modules/nginx.yml /usr/share/filebeat/modules.d/
