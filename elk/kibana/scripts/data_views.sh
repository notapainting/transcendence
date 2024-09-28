#!/bin/bash
COLOR_GREEN='\e[1;32m'
COLOR_RED='\e[1;31m'
COLOR_RESET='\e[0m'

KIBANA_URL="https://localhost:5601"

CA_CERT="/usr/share/kibana/config/certs/ca/ca.crt"

KIBANA_CERT="/usr/share/kibana/config/certs/kibana-server/kibana-server.crt"
KIBANA_KEY="/usr/share/kibana/config/certs/kibana-server/kibana-server.key" 

NGINX_JSON=$(cat /usr/share/kibana/scripts/JSON/nginx_data_view.json)
FILEBEAT_JSON=$(cat /usr/share/kibana/scripts/JSON/filebeat_data_view.json)

set -e

if [ x${ELASTIC_USER} == x ]; then
  echo "${COLOR_RED}Set the ELASTIC_USER environment variable in the .env file${COLOR_RESET}";
  exit 1;
elif [ x${ELASTIC_PASSWORD} == x ]; then
  echo "${COLOR_RED}Set the ELASTIC_PASSWORD environment variable in the .env file${COLOR_RESET}";
  exit 1;
fi

response=$(curl -X GET "$KIBANA_URL/api/data_views" \
            -u ${ELASTIC_USER}:${ELASTIC_PASSWORD}  \
            --cacert "$CA_CERT"                     \
            --cert "$KIBANA_CERT" \
            --key "$KIBANA_KEY" \
            -H 'kbn-xsrf: true')
if [[ "$response" == *"filebeat-index-*"* ]] && \
  [[ "$response" == *"nginx-index-*"* ]]; then
  echo -e "${COLOR_GREEN}All Data Views creation completed.${COLOR_RESET}"
  sleep 5
  exit 0
else
  echo -e "${COLOR_GREEN}Creating Data Views...${COLOR_RESET}"

  response=$(curl -X POST "$KIBANA_URL/api/data_views/data_view" \
  -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  --cacert "$CA_CERT" \
    --cert "$KIBANA_CERT" \
    --key "$KIBANA_KEY" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d "$NGINX_JSON")
  if [[ "$response" == *'"id":"nginx-data"'* ]]; then
    echo -e "${COLOR_GREEN}\nNginx Data View configured.${COLOR_RESET}"
  else
    echo -e "${COLOR_RED}\nIssue with Nginx Data Views creation.${COLOR_RESET}"
    exit 1;
  fi

  response=$(curl -X POST "$KIBANA_URL/api/data_views/data_view" \
  -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  --cacert "$CA_CERT" \
    --cert "$KIBANA_CERT" \
    --key "$KIBANA_KEY" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d "$FILEBEAT_JSON")
  if [[ "$response" == *'"id":"filebeat-data"'* ]]; then
    echo -e "${COLOR_GREEN}\nFilebeat Data View configured.${COLOR_RESET}"
  else
    echo -e "${COLOR_RED}\nIssue with Filebeat Data Views creation.${COLOR_RESET}"
    exit 1;
  fi

fi

echo -e "${COLOR_GREEN}\nAll Data Views creation completed.${COLOR_RESET}"

sleep 5
