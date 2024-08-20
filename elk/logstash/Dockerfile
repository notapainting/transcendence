FROM    docker.elastic.co/logstash/logstash:8.14.1


COPY    conf/logstash.conf /usr/share/logstash/pipeline/logstash.conf
COPY    conf/JSON/nginx.json /etc/logstash/nginx.json
COPY    conf/JSON/filebeat.json /etc/logstash/filebeat.json
RUN     bin/logstash-plugin update

CMD ["-f", "/usr/share/logstash/pipeline/logstash.conf"]
