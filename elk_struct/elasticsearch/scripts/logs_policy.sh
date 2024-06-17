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

if [ x${ELASTIC_USER} == x ]; then
  echo "${COLOR_RED}Set the ELASTIC_USER environment variable in the .env file${COLOR_RESET}";
  exit 1;
elif [ x${ELASTIC_PASSWORD} == x ]; then
  echo "${COLOR_RED}Set the ELASTIC_PASSWORD environment variable in the .env file${COLOR_RESET}";
  exit 1;
fi;

# Creating the ILM policy
echo -e "${COLOR_GREEN}Configuring ILM policy...${COLOR_RESET}"

curl -X PUT -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  "$ELASTICSEARCH_URL/_ilm/policy/nginx_policy?pretty" \
  -H 'Content-Type: application/json' \
  --cacert "$CA_CERT" \
  -d '{
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
response=$(curl -s -X GET -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
          "${ELASTICSEARCH_URL}/_ilm/policy/nginx_policy?pretty" \
          -H 'Content-Type: application/json' \
          --cacert "${CA_CERT}")

if [[ "$response" == *"nginx_policy"* ]]; then
  echo -e "${COLOR_GREEN}Nginx policy done.${COLOR_RESET}"
else
  echo -e "${COLOR_RED}Issue with Nginx policy configuration.${COLOR_RESET}"
  exit 1;
fi

curl -X PUT -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  "$ELASTICSEARCH_URL/_ilm/policy/logstash_policy?pretty" \
  -H 'Content-Type: application/json' \
  --cacert "$CA_CERT" \
  -d '{
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
response=$(curl -s -X GET -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
          "${ELASTICSEARCH_URL}/_ilm/policy/logstash_policy?pretty" \
          -H 'Content-Type: application/json' \
          --cacert "${CA_CERT}")

if [[ "$response" == *"logstash_policy"* ]]; then
  echo -e "${COLOR_GREEN}Logstash policy done.${COLOR_RESET}"
else
  echo -e "${COLOR_RED}Issue with Logstash policy configuration.${COLOR_RESET}"
  exit 1;
fi

curl -X PUT -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  "$ELASTICSEARCH_URL/_ilm/policy/filebeat_policy?pretty" \
  -H 'Content-Type: application/json' \
  --cacert "$CA_CERT" \
  -d '{
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

response=$(curl -s -X GET -u "${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
          "${ELASTICSEARCH_URL}/_ilm/policy/filebeat_policy?pretty" \
          -H 'Content-Type: application/json' \
          --cacert "${CA_CERT}")

if [[ "$response" == *"filebeat_policy"* ]]; then
  echo -e "${COLOR_GREEN}Filebeat policy done.${COLOR_RESET}"
else
  echo -e "${COLOR_RED}Issue with Filebeat policy configuration.${COLOR_RESET}"
  exit 1;
fi

echo -e "${COLOR_GREEN}All ILM policy configuration completed.${COLOR_RESET}"
sleep 10
