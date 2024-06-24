#!/bin/bash
COLOR_GREEN='\e[1;32m'
COLOR_RED='\e[1;31m'
COLOR_RESET='\e[0m'

ELASTIC_USER=elastic

# Define the URL for Elasticsearch
ELASTICSEARCH_URL="https://localhost:9200"

# Define the path to the CA certificate
CA_CERT="/usr/share/elasticsearch/config/certs/ca/ca.crt"

set -e

if [ -z "$ELASTIC_USER" ]; then
  echo -e "${COLOR_RED}Set the ELASTIC_USER environment variable in the .env file${COLOR_RESET}"
  exit 1
elif [ -z "$ELASTIC_PASSWORD" ]; then
  echo -e "${COLOR_RED}Set the ELASTIC_PASSWORD environment variable in the .env file${COLOR_RESET}"
  exit 1
fi

# Create the GeoIP ingest pipeline
echo -e "${COLOR_GREEN}Creating GeoIP ingest pipeline...${COLOR_RESET}"

response=$(curl -X PUT "$ELASTICSEARCH_URL/_ingest/pipeline/geoip" \
    --cacert "$CA_CERT" \
    -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
    -H 'Content-Type: application/json' \
    -d '{
    "description" : "Add GeoIP Info",
    "processors" : [
        {
        "geoip" : {
            "field" : "client_ip"
        }
        }
    ]
    }')

if [[ "$response" != *'"acknowledged" : true'* ]]; then
  echo -e "${COLOR_GREEN}GeoIP pipeline created successfully.${COLOR_RESET}"
else
  echo -e "${COLOR_RED}Issue with GeoIP pipeline creation.${COLOR_RESET}"
  exit 1
fi

# ILM policy JSON
ilm_policy_json='{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_primary_shard_size": "50GB",
            "max_age": "30d"
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "forcemerge": {
            "max_num_segments": 1
          },
          "shrink": {
            "number_of_shards": 1
          },
          "allocate": {
            "require": {
              "data": "warm"
            }
          },
          "set_priority": {
            "priority": 25
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "set_priority": {
            "priority": 0
          },
          "freeze": {},
          "allocate": {
            "require": {
              "data": "cold"
            }
          }
        }
      },
      "delete": {
        "min_age": "60d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'

# List of policy names
policy_names=("nginx_policy" "logstash_policy" "filebeat_policy")

for policy_name in "${policy_names[@]}"; do
  echo -e "${COLOR_GREEN}Configuring ILM policy for ${policy_name}...${COLOR_RESET}"
  
  response=$(curl -X PUT -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
    "$ELASTICSEARCH_URL/_ilm/policy/${policy_name}?pretty" \
    -H 'Content-Type: application/json' \
    --cacert "$CA_CERT" \
    -d "$ilm_policy_json")

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
