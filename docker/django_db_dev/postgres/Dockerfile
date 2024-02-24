FROM postgres:15-bookworm


RUN mkdir -p ${PGDATA} /logs
COPY init-script.sh /docker-entrypoint-initdb.d/

EXPOSE ${PORT}
