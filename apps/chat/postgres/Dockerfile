FROM postgres:16-alpine3.19

ENV TZ=Europe/Paris
RUN mkdir -p \
	${PGDATA} \
	/logs

COPY init-script.sh /docker-entrypoint-initdb.d/

EXPOSE ${PORT}
