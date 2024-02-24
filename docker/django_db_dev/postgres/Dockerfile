FROM postgres:16-alpine3.19

RUN mkdir -p \
	${PGDATA} \
	/logs

COPY init-script.sh /docker-entrypoint-initdb.d/

EXPOSE ${PORT}
