FROM hashicorp/vault:1.15

COPY conf/conf.json /vault/config/
COPY conf/entrypoint.sh /docker-entrypoint/
COPY conf/unseal.sh /docker-entrypoint/


# ENTRYPOINT ["/usr/bin/dumb-init", "/bin/sh", "/usr/local/bin/docker-entrypoint.sh", "server", "-ed"]
# CMD ["vault", "server", "-config=/vault/config/conf.json"]
# CMD ["/usr/bin/dumb-init", "/bin/sh", "docker-entrypoint/unseal.sh"]
