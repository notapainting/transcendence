FROM hashicorp/vault:1.15


RUN apk add --no-cache curl vim

COPY unseal.sh /docker-entrypoint/

ENTRYPOINT /usr/bin/dumb-init /bin/sh /docker-entrypoint/unseal.sh
