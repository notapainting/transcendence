FROM    docker.elastic.co/logstash/logstash:8.14.1


COPY    conf/logstash.conf /usr/share/logstash/pipeline/logstash.conf
COPY    conf/nginx.json /etc/logstash/nginx.json
COPY    conf/logstash.json /etc/logstash/logstash.json
COPY    conf/filebeat.json /etc/logstash/filebeat.json


CMD ["-f", "/usr/share/logstash/pipeline/logstash.conf"]
