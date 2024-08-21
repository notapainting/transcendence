#!/bin/bash
COLOR_GREEN='\e[1;32m'
COLOR_RED='\e[1;31m'
COLOR_RESET='\e[0m'

# Define the URL for Elasticsearch
ELASTICSEARCH_URL="https://localhost:9200"

# Define the path to the CA certificate
CA_CERT="/usr/share/elasticsearch/config/certs/ca/ca.crt"

set -e

# ILM policy JSON
ILM_JSON=$(cat /usr/share/elasticsearch/scripts/ilm.json)

# List of policy names
policy_names=("nginx_policy" "filebeat_policy")

for policy_name in "${policy_names[@]}"; do
  echo -e "${COLOR_GREEN}Configuring ILM policy for ${policy_name}...${COLOR_RESET}"
  
  response=$(curl -X PUT -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
    "$ELASTICSEARCH_URL/_ilm/policy/${policy_name}?pretty" \
    -H 'Content-Type: application/json' \
    --cacert "$CA_CERT" \
    -d "$ILM_JSON")

  if [[ "$response" != *'"acknowledged" : true'* ]]; then
    echo -e "${COLOR_RED}Issue with ${policy_name} policy configuration.${COLOR_RESET}"
    echo -e "${COLOR_RED}Response: $response${COLOR_RESET}"
    exit 1
  else
    echo -e "${COLOR_GREEN}${policy_name} policy done.${COLOR_RESET}"
  fi
done

echo -e "${COLOR_GREEN}All ILM policy configurations completed.${COLOR_RESET}"
sleep 5
