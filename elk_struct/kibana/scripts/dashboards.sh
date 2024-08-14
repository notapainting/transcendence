#!/bin/bash
COLOR_GREEN='\e[1;32m'
COLOR_RED='\e[1;31m'
COLOR_RESET='\e[0m'


# Define the URL for Elasticsearch
KIBANA_URL="https://localhost:5601"

# Define the path to the CA certificate
CA_CERT="/usr/share/kibana/config/certs/ca/ca.crt"

# Define the path to the Kibana server certificate and key
KIBANA_CERT="/usr/share/kibana/config/certs/kibana-server/kibana-server.crt"
KIBANA_KEY="/usr/share/kibana/config/certs/kibana-server/kibana-server.key"

set -e
echo -e "${COLOR_GREEN}Creating Dashboards...${COLOR_RESET}"

  response=$(curl -X POST "$KIBANA_URL/api/kibana/dashboards/import?exclude=index-pattern" \
  -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  --cacert "$CA_CERT" \
  --cert "$KIBANA_CERT" \
  --key "$KIBANA_KEY" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
    -d "$(cat /usr/share/kibana/scripts/dash.json)")
