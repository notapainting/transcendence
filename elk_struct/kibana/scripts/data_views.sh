#!/bin/bash
COLOR_GREEN='\e[1;32m'
COLOR_RED='\e[1;31m'
COLOR_RESET='\e[0m'

# Define the URL for Elasticsearch
KIBANA_URL="localhost:5601"

# Define the path to the CA certificate
CA_CERT="/usr/share/kibana/config/certs/ca/ca.crt"

KIBANA_CERT="/usr/share/kibana/config/certs/kibana-server/kibana-server.crt"
KIBANA_KEY="/usr/share/kibana/config/certs/kibana-server/kibana-server.key" 

nginx_data_view='{
  "data_view": {
    "title": "nginx-index-*",
    "name": "My Nginx Data View",
    "id": "nginx-data",
    "fieldAttrs": {
      "@timestamp": {
        "customLabel": "Timestamp"
      },
      "client_ip": {
        "customLabel": "Client IP"
      },
      "method": {
        "customLabel": "Method"
      },
      "request": {
        "customLabel": "Request"
      },
      "status_code": {
        "customLabel": "Status Code"
      },
      "user_agent": {
        "customLabel": "User Agent"
      },
      "response_size": {
        "customLabel": "Response Size"
      },
      "log_type": {
        "customLabel": "Log Type"
      },
      "geoip.location": {
        "customLabel": "GeoIP Location"
      },
      "geoip.city_name": {
        "customLabel": "GeoIP City Name"
      },
      "geoip.continent_name": {
        "customLabel": "GeoIP Continent Name"
      },
      "geoip.country_iso_code": {
        "customLabel": "GeoIP Country ISO Code"
      },
      "geoip.country_name": {
        "customLabel": "GeoIP Country Name"
      }
    }
  }
}'


logstash_data_view='{
  "data_view": {
    "title": "logstash-index-*",
    "name": "My Logstash Data View",
    "id": "logstash-data",
    "fieldAttrs": {
      "timestamp": {
        "customLabel": "Timestamp"
      },
      "program": {
        "customLabel": "Program"
      },
      "syslog_message": {
        "customLabel": "Message"
      }
    }
  }
}'

filebeat_data_view='{
  "data_view": {
    "title": "filebeat-index-*",
    "name": "My Filebeat Data View",
    "id": "filebeat-data",
    "fieldAttrs": {
      "timestamp": {
        "customLabel": "Timestamp"
      },
      "program": {
        "customLabel": "Program"
      },
      "syslog_message": {
        "customLabel": "Message"
      }
    }
  }
}'

set -e

if [ x${ELASTIC_USER} == x ]; then
  echo "${COLOR_RED}Set the ELASTIC_USER environment variable in the .env file${COLOR_RESET}";
  exit 1;
elif [ x${ELASTIC_PASSWORD} == x ]; then
  echo "${COLOR_RED}Set the ELASTIC_PASSWORD environment variable in the .env file${COLOR_RESET}";
  exit 1;
fi

# Creating Data Views
response=$(curl -X GET "$KIBANA_URL/api/data_views" \
            -u ${ELASTIC_USER}:${ELASTIC_PASSWORD}  \
            --cacert "$CA_CERT"                     \
            --cert "$KIBANA_CERT" \
            --key "$KIBANA_KEY" \
            -H 'kbn-xsrf: true')
if [[ "$response" == *"filebeat-index-*"* ]] && \
  [[ "$response" == *"logstash-index-*"* ]] && \
  [[ "$response" == *"nginx-index-*"* ]]; then
  echo -e "${COLOR_GREEN}All Data Views creation completed.${COLOR_RESET}"
  sleep 5
  exit 0
else
  echo -e "${COLOR_GREEN}Creating Data Views...${COLOR_RESET}"

# Creating Nginx Data View
  response=$(curl -X POST "$KIBANA_URL/api/data_views/data_view" \
  -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  --cacert "$CA_CERT" \
    --cert "$KIBANA_CERT" \
    --key "$KIBANA_KEY" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d "$nginx_data_view")
  if [[ "$response" == *'"id":"nginx-data"'* ]]; then
    echo -e "${COLOR_GREEN}\nNginx Data View configured.${COLOR_RESET}"
  else
    echo -e "${COLOR_RED}\nIssue with Nginx Data Views creation.${COLOR_RESET}"
    exit 1;
  fi

# Creating Logstash Data View
  response=$(curl -X POST "$KIBANA_URL/api/data_views/data_view" \
  -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  --cacert "$CA_CERT" \
    --cert "$KIBANA_CERT" \
    --key "$KIBANA_KEY" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d "$logstash_data_view")
  if [[ "$response" == *'"id":"logstash-data"'* ]]; then
    echo -e "${COLOR_GREEN}\nLogstash Data View configured.${COLOR_RESET}"
  else
    echo -e "${COLOR_RED}\nIssue with Logstash Data Views creation.${COLOR_RESET}"
    exit 1;
  fi

# Creating Filebeat Data View
  response=$(curl -X POST "$KIBANA_URL/api/data_views/data_view" \
  -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  --cacert "$CA_CERT" \
    --cert "$KIBANA_CERT" \
    --key "$KIBANA_KEY" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d "$filebeat_data_view")
  if [[ "$response" == *'"id":"filebeat-data"'* ]]; then
    echo -e "${COLOR_GREEN}\nFilebeat Data View configured.${COLOR_RESET}"
  else
    echo -e "${COLOR_RED}\nIssue with Filebeat Data Views creation.${COLOR_RESET}"
    exit 1;
  fi

fi

echo -e "${COLOR_GREEN}\nAll Data Views creation completed.${COLOR_RESET}"

sleep 5
