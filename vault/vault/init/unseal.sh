#!/usr/bin/dumb-init /bin/sh

echo `date` "unsealing key 1"
vault operator unseal ${UKEY1}

echo `date` "unsealing key 2"
vault operator unseal ${UKEY2}

echo `date` "unsealing key 3"
vault operator unseal ${UKEY3}

