FROM postgres:15-bookworm

ARG PORT

RUN echo >> /var/lib/postgresql/data/postgresql.conf "port = "${PORT}

EXPOSE ${PORT}
