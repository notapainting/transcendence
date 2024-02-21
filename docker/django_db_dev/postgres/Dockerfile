FROM postgres:15-bookworm

ARG PORT

RUN echo >> /var/lib/postgresql/data/postgresql.conf "port = "${PORT}
RUN mkdir -p /var/lib/postgresql/data/

EXPOSE ${PORT}
