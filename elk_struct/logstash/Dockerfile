FROM    docker.elastic.co/logstash/logstash:8.12.2

COPY    conf/logstash.conf /usr/share/logstash/pipeline/logstash.conf

CMD ["-f", "/usr/share/logstash/pipeline/logstash.conf"]
