#!/usr/bin/dumb-init /bin/sh

# su-exec vault vault server -config=/vault/config/conf.json 

sleep 2

echo "unsealing vault"

vault operator unseal ${UKEY1}
vault operator unseal ${UKEY2}
vault operator unseal ${UKEY3}

# exec "vault server -config=/vault/config/local.json"
