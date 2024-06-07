FROM postgres:16-alpine3.19

ENV PGDATA=/var/lib/postgresql/data/

RUN mkdir -p \
	${PGDATA} 

COPY init-script.sh /docker-entrypoint-initdb.d/

EXPOSE ${PORT}
