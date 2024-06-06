ui            = true
cluster_addr  = "https://127.0.0.1:8201"
api_addr      = "https://127.0.0.1:8200"
disable_mlock = false

default_lease_ttl = "56h"
max_lease_ttl = "168h"

log_format = "standard" // can be json

storage "file" {
  path = "/vault/file"
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_disable   = "true"
}



# telemetry {
#   statsite_address = "127.0.0.1:8125"
#   disable_hostname = true
# }
