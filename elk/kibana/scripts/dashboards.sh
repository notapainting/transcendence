#!/bin/bash
COLOR_GREEN='\e[1;32m'
COLOR_RED='\e[1;31m'
COLOR_RESET='\e[0m'

KIBANA_URL="https://localhost:5601"

CA_CERT="/usr/share/kibana/config/certs/ca/ca.crt"

KIBANA_CERT="/usr/share/kibana/config/certs/kibana-server/kibana-server.crt"
KIBANA_KEY="/usr/share/kibana/config/certs/kibana-server/kibana-server.key"

set -e

response=$(curl -X GET "$KIBANA_URL/api/kibana/dashboards/export?dashboard=29164c80-2f93-489d-b25f-4ea20996f230" \
                -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
                --cacert "$CA_CERT" \
                --cert "$KIBANA_CERT" \
                --key "$KIBANA_KEY" \
                -H 'kbn-xsrf: true')

if [[ "$response" == *'"title":"Bill Dashboard"'* ]]; then
  echo -e "${COLOR_GREEN}All Dashboards creation completed.${COLOR_RESET}"
  exit 0
else
  echo -e "${COLOR_GREEN}Creating Dashboards...${COLOR_RESET}"

  DASHBOARD_JSON=$(cat /usr/share/kibana/scripts/JSON/dash.json)

  response=$(curl -X POST "$KIBANA_URL/api/kibana/dashboards/import?exclude=index-pattern" \
  -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  --cacert "$CA_CERT" \
  --cert "$KIBANA_CERT" \
  --key "$KIBANA_KEY" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d "$DASHBOARD_JSON")
fi

