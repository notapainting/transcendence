FROM postgres:15-bookworm

ARG PORT
ARG PGDIR

RUN mkdir -p ${PGDIR}
COPY init-script.sh /docker-entrypoint-initdb.d/

EXPOSE ${PORT}
