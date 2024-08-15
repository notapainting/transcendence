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

# # Check Dashboards existance
# response=$(curl -X GET "$KIBANA_URL/api/kibana/dashboards/export?dashboard=29164c80-2f93-489d-b25f-4ea20996f230" \
#                 -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
#                 --cacert "$CA_CERT" \
#                 --cert "$KIBANA_CERT" \
#                 --key "$KIBANA_KEY" \
#                 -H 'kbn-xsrf: true')

# if [[ "$response" == *"Bill Dashboard"* ]]; then
#   echo -e "${COLOR_GREEN}All Dashboards creation completed.${COLOR_RESET}"
#   exit 0
# else
  echo -e "${COLOR_GREEN}Creating Dashboards...${COLOR_RESET}"

  DASHBOARD_JSON=$(cat /usr/share/kibana/scripts/dash.json)
# Creating Dashboards
  response=$(curl -X POST "$KIBANA_URL/api/kibana/dashboards/import?exclude=index-pattern" \
  -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
  --cacert "$CA_CERT" \
  --cert "$KIBANA_CERT" \
  --key "$KIBANA_KEY" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
    -d "$DASHBOARD_JSON")

# # Creating Dashboards
#   response=$(curl -X POST "$KIBANA_URL/api/kibana/dashboards/import?exclude=index-pattern" \
#   -u ${ELASTIC_USER}:${ELASTIC_PASSWORD} \
#   --cacert "$CA_CERT" \
#   --cert "$KIBANA_CERT" \
#   --key "$KIBANA_KEY" \
#   -H 'kbn-xsrf: true' \
#   -H 'Content-Type: application/json' \
#     -d'
#   {
#     "version": "8.14.1",
#     "objects": [
#       {
#         "id": "29164c80-2f93-489d-b25f-4ea20996f230",
#         "type": "dashboard",
#         "namespaces": [
#           "default"
#         ],
#         "updated_at": "2024-08-14T11:38:43.167Z",
#         "created_at": "2024-08-14T11:04:11.363Z",
#         "version": "WzE0MywxXQ==",
#         "attributes": {
#           "version": 2,
#           "kibanaSavedObjectMeta": {
#             "searchSourceJSON": "{\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filter\":[]}"
#           },
#           "description": "",
#           "refreshInterval": {
#             "pause": true,
#             "value": 60000
#           },
#           "timeRestore": true,
#           "optionsJSON": "{\"useMargins\":true,\"syncColors\":false,\"syncCursor\":true,\"syncTooltips\":false,\"hidePanelTitles\":false}",
#           "panelsJSON":"[{\"type\":\"visualization\",\"gridData\":{\"x\":0,\"y\":0,\"w\":11,\"h\":17,\"i\":\"0a9d9f3c-21f1-4301-860f-c33f0622de04\"},\"panelIndex\":\"0a9d9f3c-21f1-4301-860f-c33f0622de04\",\"embeddableConfig\":{\"savedVis\":{\"id\":\"\",\"title\":\"\",\"description\":\"\",\"type\":\"markdown\",\"params\":{\"fontSize\":12,\"openLinksInNewTab\":false,\"markdown\":\"### Introduction au concept du dashboard sur Kibana\\n\\nUn **dashboard** dans **Kibana** est un outil puissant qui permet de visualiser et de surveiller des données en temps réel à partir de différentes sources. \\n\\n### Explication des panneaux visibles\\n\\n1. **Carte de chaleur par catégorie d'utilisateur (en haut à gauche) :**\\n   Ce panneau utilise une visualisation en mosaïque pour représenter les différentes catégories d'utilisateurs (telles que *user*, *proxy*, *chat*, etc.). La taille de chaque carré semble être proportionnelle au nombre d'événements ou d'occurrences pour chaque catégorie, ce qui permet de voir rapidement quelle catégorie domine.\\n\\n2. **Répartition des codes de statut HTTP (en haut au centre) :**\\n   Cette visualisation montre une répartition des différentes réponses HTTP par code de statut. On observe une large section dédiée aux erreurs 500, indiquant un problème majeur avec un endpoint spécifique, probablement le plus fréquenté. Cela permet d’identifier les principaux points de défaillance.\\n\\n3. **Tableau des requêtes HTTP (en haut à droite) :**\\n   Ce tableau liste les requêtes HTTP avec les colonnes telles que *Timestamp*, *Page URL* et *Status Code*. Il montre en détail les requêtes récentes, offrant un suivi précis des accès et des réponses, ce qui est crucial pour le débogage en temps réel.\\n\\n4. **Carte géographique des événements (en bas à gauche) :**\\n   Cette carte montre la répartition géographique des événements ou des connexions. Elle est utile pour comprendre la provenance des utilisateurs et identifier les zones géographiques où les anomalies peuvent se produire.\\n\\n5. **Graphique temporel des événements (en bas à droite) :**\\n   Ce panneau présente un graphique temporel montrant l’évolution des événements sur un intervalle de temps, avec une distinction par catégorie (comme *user*, *proxy*, etc.). Cela permet de visualiser les tendances et les pics d'activité sur une échelle temporelle, facilitant la détection d'anomalies.\"},\"uiState\":{},\"data\":{\"aggs\":[],\"searchSource\":{\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filter\":[]}}},\"hidePanelTitles\":true,\"description\":\"\",\"enhancements\":{}},\"title\":\"\"},{\"type\":\"lens\",\"gridData\":{\"x\":35,\"y\":0,\"w\":13,\"h\":17,\"i\":\"f8793849-1980-4eb9-b3a1-44efb52ab9db\"},\"panelIndex\":\"f8793849-1980-4eb9-b3a1-44efb52ab9db\",\"embeddableConfig\":{\"attributes\":{\"title\":\"\",\"visualizationType\":\"lnsDatatable\",\"type\":\"lens\",\"references\":[{\"type\":\"index-pattern\",\"id\":\"nginx-data\",\"name\":\"indexpattern-datasource-layer-96752761-1420-48d0-80bb-b4950f842e37\"}],\"state\":{\"visualization\":{\"layerId\":\"96752761-1420-48d0-80bb-b4950f842e37\",\"layerType\":\"data\",\"columns\":[{\"isTransposed\":false,\"columnId\":\"266f1f7c-aedc-42cf-ac52-c517db169c65\"},{\"isTransposed\":false,\"columnId\":\"579fbfcd-6032-4b8b-9f3d-27a1797a3385\",\"isMetric\":false},{\"columnId\":\"48459d93-571e-493e-a4d8-7029bd6606d8\",\"isTransposed\":false,\"isMetric\":true,\"alignment\":\"center\"}]},\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filters\":[],\"datasourceStates\":{\"formBased\":{\"layers\":{\"96752761-1420-48d0-80bb-b4950f842e37\":{\"columns\":{\"266f1f7c-aedc-42cf-ac52-c517db169c65\":{\"label\":\"Page URL\",\"dataType\":\"string\",\"operationType\":\"terms\",\"scale\":\"ordinal\",\"sourceField\":\"request.keyword\",\"isBucketed\":true,\"params\":{\"size\":999,\"orderBy\":{\"type\":\"column\",\"columnId\":\"48459d93-571e-493e-a4d8-7029bd6606d8\"},\"orderDirection\":\"desc\",\"otherBucket\":false,\"missingBucket\":false,\"parentFormat\":{\"id\":\"terms\"},\"include\":[],\"exclude\":[],\"includeIsRegex\":false,\"excludeIsRegex\":false},\"customLabel\":true},\"579fbfcd-6032-4b8b-9f3d-27a1797a3385\":{\"label\":\"Timestamp\",\"dataType\":\"date\",\"operationType\":\"date_histogram\",\"sourceField\":\"@timestamp\",\"isBucketed\":true,\"scale\":\"interval\",\"params\":{\"interval\":\"ms\",\"includeEmptyRows\":false,\"dropPartials\":false,\"ignoreTimeRange\":true}},\"48459d93-571e-493e-a4d8-7029bd6606d8\":{\"label\":\"Status Code\",\"dataType\":\"number\",\"operationType\":\"last_value\",\"isBucketed\":false,\"scale\":\"ratio\",\"sourceField\":\"status_code\",\"filter\":{\"query\":\"\\\"status_code\\\": *\",\"language\":\"kuery\"},\"params\":{\"sortField\":\"@timestamp\"},\"customLabel\":true}},\"columnOrder\":[\"579fbfcd-6032-4b8b-9f3d-27a1797a3385\",\"266f1f7c-aedc-42cf-ac52-c517db169c65\",\"48459d93-571e-493e-a4d8-7029bd6606d8\"],\"incompleteColumns\":{},\"sampling\":1,\"indexPatternId\":\"nginx-data\"}},\"currentIndexPatternId\":\"nginx-data\"},\"indexpattern\":{\"layers\":{}},\"textBased\":{\"layers\":{}}},\"internalReferences\":[],\"adHocDataViews\":{}}},\"hidePanelTitles\":true,\"enhancements\":{}},\"title\":\"\"},{\"type\":\"lens\",\"gridData\":{\"x\":11,\"y\":0,\"w\":11,\"h\":17,\"i\":\"7407168a-661c-47b4-8203-b567fa250da0\"},\"panelIndex\":\"7407168a-661c-47b4-8203-b567fa250da0\",\"embeddableConfig\":{\"attributes\":{\"title\":\"\",\"visualizationType\":\"lnsPie\",\"type\":\"lens\",\"references\":[{\"type\":\"index-pattern\",\"id\":\"filebeat-data\",\"name\":\"indexpattern-datasource-layer-14241a35-d1e3-4b07-bba5-dc554c9931ec\"}],\"state\":{\"visualization\":{\"shape\":\"waffle\",\"layers\":[{\"layerId\":\"14241a35-d1e3-4b07-bba5-dc554c9931ec\",\"primaryGroups\":[\"38834063-d4ad-4449-a655-1d77362fa434\"],\"metrics\":[\"c8bf37d9-9558-4861-8d0d-830cf24253df\"],\"numberDisplay\":\"percent\",\"categoryDisplay\":\"default\",\"legendDisplay\":\"default\",\"nestedLegend\":false,\"layerType\":\"data\",\"colorMapping\":{\"assignments\":[],\"specialAssignments\":[{\"rule\":{\"type\":\"other\"},\"color\":{\"type\":\"loop\"},\"touched\":false}],\"paletteId\":\"eui_amsterdam_color_blind\",\"colorMode\":{\"type\":\"categorical\"}}}]},\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filters\":[],\"datasourceStates\":{\"formBased\":{\"layers\":{\"14241a35-d1e3-4b07-bba5-dc554c9931ec\":{\"columns\":{\"38834063-d4ad-4449-a655-1d77362fa434\":{\"label\":\"Conteneur called\",\"dataType\":\"string\",\"operationType\":\"terms\",\"scale\":\"ordinal\",\"sourceField\":\"container.name\",\"isBucketed\":true,\"params\":{\"size\":1000,\"orderBy\":{\"type\":\"column\",\"columnId\":\"c8bf37d9-9558-4861-8d0d-830cf24253df\"},\"orderDirection\":\"desc\",\"otherBucket\":false,\"missingBucket\":false,\"parentFormat\":{\"id\":\"terms\"},\"include\":[],\"exclude\":[],\"includeIsRegex\":false,\"excludeIsRegex\":false},\"customLabel\":true},\"c8bf37d9-9558-4861-8d0d-830cf24253df\":{\"label\":\"Count of records\",\"dataType\":\"number\",\"operationType\":\"count\",\"isBucketed\":false,\"scale\":\"ratio\",\"sourceField\":\"___records___\",\"params\":{\"emptyAsNull\":true}}},\"columnOrder\":[\"38834063-d4ad-4449-a655-1d77362fa434\",\"c8bf37d9-9558-4861-8d0d-830cf24253df\"],\"incompleteColumns\":{},\"sampling\":1}}},\"indexpattern\":{\"layers\":{}},\"textBased\":{\"layers\":{}}},\"internalReferences\":[],\"adHocDataViews\":{}}},\"hidePanelTitles\":true,\"enhancements\":{}},\"title\":\"\"},{\"type\":\"lens\",\"gridData\":{\"x\":22,\"y\":0,\"w\":13,\"h\":17,\"i\":\"7694390b-442d-46ad-a330-2a6179e43616\"},\"panelIndex\":\"7694390b-442d-46ad-a330-2a6179e43616\",\"embeddableConfig\":{\"attributes\":{\"title\":\"\",\"visualizationType\":\"lnsPie\",\"type\":\"lens\",\"references\":[{\"type\":\"index-pattern\",\"id\":\"nginx-data\",\"name\":\"indexpattern-datasource-layer-083dad48-0631-4306-b237-ca6ea9ddb4c6\"}],\"state\":{\"visualization\":{\"shape\":\"treemap\",\"layers\":[{\"layerId\":\"083dad48-0631-4306-b237-ca6ea9ddb4c6\",\"primaryGroups\":[\"f9b8effd-8500-4420-92cd-89fb1ddfdce6\",\"1de7e567-045e-4a38-96c0-e3f47930d09d\"],\"secondaryGroups\":[],\"metrics\":[\"323b9384-e68b-4254-9948-5c591715eee1\"],\"numberDisplay\":\"percent\",\"categoryDisplay\":\"default\",\"legendDisplay\":\"default\",\"nestedLegend\":false,\"layerType\":\"data\",\"colorMapping\":{\"assignments\":[],\"specialAssignments\":[{\"rule\":{\"type\":\"other\"},\"color\":{\"type\":\"loop\"},\"touched\":false}],\"paletteId\":\"eui_amsterdam_color_blind\",\"colorMode\":{\"type\":\"categorical\"}}}]},\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filters\":[],\"datasourceStates\":{\"formBased\":{\"layers\":{\"083dad48-0631-4306-b237-ca6ea9ddb4c6\":{\"columns\":{\"f9b8effd-8500-4420-92cd-89fb1ddfdce6\":{\"label\":\"Status Code Except 200\",\"dataType\":\"number\",\"operationType\":\"terms\",\"scale\":\"ordinal\",\"sourceField\":\"status_code\",\"isBucketed\":true,\"params\":{\"size\":1000,\"orderBy\":{\"type\":\"column\",\"columnId\":\"323b9384-e68b-4254-9948-5c591715eee1\"},\"orderDirection\":\"desc\",\"otherBucket\":false,\"missingBucket\":false,\"parentFormat\":{\"id\":\"terms\"},\"include\":[],\"exclude\":[],\"includeIsRegex\":false,\"excludeIsRegex\":false,\"secondaryFields\":[]},\"customLabel\":true},\"323b9384-e68b-4254-9948-5c591715eee1\":{\"label\":\"Timestamp\",\"dataType\":\"number\",\"operationType\":\"count\",\"isBucketed\":false,\"scale\":\"ratio\",\"sourceField\":\"@timestamp\",\"filter\":{\"query\":\"status_code >= 201\",\"language\":\"kuery\"},\"params\":{\"emptyAsNull\":true}},\"1de7e567-045e-4a38-96c0-e3f47930d09d\":{\"label\":\"Top 1000 values of request.keyword\",\"dataType\":\"string\",\"operationType\":\"terms\",\"scale\":\"ordinal\",\"sourceField\":\"request.keyword\",\"isBucketed\":true,\"params\":{\"size\":1000,\"orderBy\":{\"type\":\"column\",\"columnId\":\"323b9384-e68b-4254-9948-5c591715eee1\"},\"orderDirection\":\"desc\",\"otherBucket\":false,\"missingBucket\":false,\"parentFormat\":{\"id\":\"terms\"},\"include\":[],\"exclude\":[],\"includeIsRegex\":false,\"excludeIsRegex\":false}}},\"columnOrder\":[\"f9b8effd-8500-4420-92cd-89fb1ddfdce6\",\"1de7e567-045e-4a38-96c0-e3f47930d09d\",\"323b9384-e68b-4254-9948-5c591715eee1\"],\"sampling\":1,\"ignoreGlobalFilters\":false,\"incompleteColumns\":{},\"indexPatternId\":\"nginx-data\"}},\"currentIndexPatternId\":\"nginx-data\"},\"indexpattern\":{\"layers\":{}},\"textBased\":{\"layers\":{}}},\"internalReferences\":[],\"adHocDataViews\":{}}},\"hidePanelTitles\":true,\"enhancements\":{}},\"title\":\"\"},{\"type\":\"lens\",\"gridData\":{\"x\":0,\"y\":17,\"w\":22,\"h\":15,\"i\":\"80d8ead3-41c7-419b-96e4-ab4cbf09168d\"},\"panelIndex\":\"80d8ead3-41c7-419b-96e4-ab4cbf09168d\",\"embeddableConfig\":{\"attributes\":{\"title\":\"\",\"visualizationType\":\"lnsChoropleth\",\"type\":\"lens\",\"references\":[{\"type\":\"index-pattern\",\"id\":\"nginx-data\",\"name\":\"indexpattern-datasource-layer-df7a855f-b402-4b0a-8ea5-97a80ca71104\"}],\"state\":{\"visualization\":{\"layerId\":\"df7a855f-b402-4b0a-8ea5-97a80ca71104\",\"layerType\":\"data\",\"valueAccessor\":\"448573d3-9de4-4a59-bd10-bb898256d75c\",\"regionAccessor\":\"323a51e0-db7b-4658-8ba8-9e0918555b65\"},\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filters\":[],\"datasourceStates\":{\"formBased\":{\"layers\":{\"df7a855f-b402-4b0a-8ea5-97a80ca71104\":{\"columns\":{\"448573d3-9de4-4a59-bd10-bb898256d75c\":{\"label\":\"Unique count of Client IP\",\"dataType\":\"number\",\"operationType\":\"unique_count\",\"scale\":\"ratio\",\"sourceField\":\"client_ip\",\"isBucketed\":false,\"params\":{\"emptyAsNull\":true}},\"323a51e0-db7b-4658-8ba8-9e0918555b65\":{\"label\":\"Top 5 values of hour_of_day\",\"dataType\":\"string\",\"operationType\":\"terms\",\"scale\":\"ordinal\",\"sourceField\":\"hour_of_day\",\"isBucketed\":true,\"params\":{\"size\":5,\"orderBy\":{\"type\":\"column\",\"columnId\":\"448573d3-9de4-4a59-bd10-bb898256d75c\"},\"orderDirection\":\"desc\",\"otherBucket\":true,\"missingBucket\":false,\"parentFormat\":{\"id\":\"terms\"},\"include\":[],\"exclude\":[],\"includeIsRegex\":false,\"excludeIsRegex\":false}}},\"columnOrder\":[\"323a51e0-db7b-4658-8ba8-9e0918555b65\",\"448573d3-9de4-4a59-bd10-bb898256d75c\"],\"sampling\":1,\"ignoreGlobalFilters\":false,\"incompleteColumns\":{}}}},\"indexpattern\":{\"layers\":{}},\"textBased\":{\"layers\":{}}},\"internalReferences\":[],\"adHocDataViews\":{}}},\"enhancements\":{}}},{\"type\":\"lens\",\"gridData\":{\"x\":22,\"y\":17,\"w\":26,\"h\":15,\"i\":\"feb68c14-44a8-4d0d-8043-480eb964c782\"},\"panelIndex\":\"feb68c14-44a8-4d0d-8043-480eb964c782\",\"embeddableConfig\":{\"attributes\":{\"title\":\"\",\"visualizationType\":\"lnsXY\",\"type\":\"lens\",\"references\":[{\"type\":\"index-pattern\",\"id\":\"filebeat-data\",\"name\":\"indexpattern-datasource-layer-1ea590b8-28dc-45d2-82ec-d9f81612bc60\"}],\"state\":{\"visualization\":{\"legend\":{\"isVisible\":true,\"position\":\"right\"},\"valueLabels\":\"hide\",\"fittingFunction\":\"None\",\"axisTitlesVisibilitySettings\":{\"x\":true,\"yLeft\":true,\"yRight\":true},\"tickLabelsVisibilitySettings\":{\"x\":true,\"yLeft\":true,\"yRight\":true},\"labelsOrientation\":{\"x\":0,\"yLeft\":0,\"yRight\":0},\"gridlinesVisibilitySettings\":{\"x\":true,\"yLeft\":true,\"yRight\":true},\"preferredSeriesType\":\"bar_horizontal_stacked\",\"layers\":[{\"layerId\":\"1ea590b8-28dc-45d2-82ec-d9f81612bc60\",\"seriesType\":\"bar_horizontal_stacked\",\"xAccessor\":\"6b3d1c6a-3de9-48c8-9bd4-d8ef78cc0127\",\"splitAccessor\":\"22fe947b-c8e4-44a9-b691-feff41bf0498\",\"accessors\":[\"1fd48847-6235-447f-b7d3-0306cd53cde5\"],\"layerType\":\"data\",\"colorMapping\":{\"assignments\":[],\"specialAssignments\":[{\"rule\":{\"type\":\"other\"},\"color\":{\"type\":\"loop\"},\"touched\":false}],\"paletteId\":\"eui_amsterdam_color_blind\",\"colorMode\":{\"type\":\"categorical\"}}}]},\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filters\":[],\"datasourceStates\":{\"formBased\":{\"layers\":{\"1ea590b8-28dc-45d2-82ec-d9f81612bc60\":{\"columns\":{\"1fd48847-6235-447f-b7d3-0306cd53cde5\":{\"label\":\"Count of records\",\"dataType\":\"number\",\"operationType\":\"count\",\"isBucketed\":false,\"scale\":\"ratio\",\"sourceField\":\"___records___\",\"params\":{\"emptyAsNull\":true}},\"6b3d1c6a-3de9-48c8-9bd4-d8ef78cc0127\":{\"label\":\"Timestamp\",\"dataType\":\"date\",\"operationType\":\"date_histogram\",\"sourceField\":\"@timestamp\",\"isBucketed\":true,\"scale\":\"interval\",\"params\":{\"interval\":\"auto\",\"includeEmptyRows\":false,\"dropPartials\":false,\"ignoreTimeRange\":false},\"customLabel\":true},\"22fe947b-c8e4-44a9-b691-feff41bf0498\":{\"label\":\"Program\",\"dataType\":\"string\",\"operationType\":\"terms\",\"scale\":\"ordinal\",\"sourceField\":\"program\",\"isBucketed\":true,\"params\":{\"size\":1000,\"orderBy\":{\"type\":\"column\",\"columnId\":\"1fd48847-6235-447f-b7d3-0306cd53cde5\"},\"orderDirection\":\"desc\",\"otherBucket\":false,\"missingBucket\":false,\"parentFormat\":{\"id\":\"terms\"},\"include\":[],\"exclude\":[],\"includeIsRegex\":false,\"excludeIsRegex\":false},\"customLabel\":true}},\"columnOrder\":[\"22fe947b-c8e4-44a9-b691-feff41bf0498\",\"6b3d1c6a-3de9-48c8-9bd4-d8ef78cc0127\",\"1fd48847-6235-447f-b7d3-0306cd53cde5\"],\"incompleteColumns\":{},\"sampling\":1}}},\"indexpattern\":{\"layers\":{}},\"textBased\":{\"layers\":{}}},\"internalReferences\":[],\"adHocDataViews\":{}}},\"hidePanelTitles\":true,\"enhancements\":{}},\"title\":\"\"}]",
#           "timeFrom": "now-1h",
#           "title": "Bill Dashboard",
#           "timeTo": "now"
#         },
#         "references": [
#           {
#             "id": "nginx-data",
#             "name": "f8793849-1980-4eb9-b3a1-44efb52ab9db:indexpattern-datasource-layer-96752761-1420-48d0-80bb-b4950f842e37",
#             "type": "index-pattern"
#           },
#           {
#             "id": "filebeat-data",
#             "name": "7407168a-661c-47b4-8203-b567fa250da0:indexpattern-datasource-layer-14241a35-d1e3-4b07-bba5-dc554c9931ec",
#             "type": "index-pattern"
#           },
#           {
#             "id": "nginx-data",
#             "name": "7694390b-442d-46ad-a330-2a6179e43616:indexpattern-datasource-layer-083dad48-0631-4306-b237-ca6ea9ddb4c6",
#             "type": "index-pattern"
#           },
#           {
#             "id": "nginx-data",
#             "name": "80d8ead3-41c7-419b-96e4-ab4cbf09168d:indexpattern-datasource-layer-df7a855f-b402-4b0a-8ea5-97a80ca71104",
#             "type": "index-pattern"
#           },
#           {
#             "id": "filebeat-data",
#             "name": "feb68c14-44a8-4d0d-8043-480eb964c782:indexpattern-datasource-layer-1ea590b8-28dc-45d2-82ec-d9f81612bc60",
#             "type": "index-pattern"
#           }
#         ],
#         "managed": false,
#         "coreMigrationVersion": "8.8.0",
#         "typeMigrationVersion": "10.2.0"
#       },
#       {
#         "id": "nginx-data",
#         "type": "index-pattern",
#         "namespaces": [
#             "default"
#         ],
#         "updated_at": "2024-08-14T09:04:09.098Z",
#         "created_at": "2024-08-14T09:04:09.098Z",
#         "version": "WzUsMV0=",
#         "attributes" : {
#           "fieldAttrs": "{\"client_ip\":{\"customLabel\":\"Client IP\"},\"method\":{\"customLabel\":\"Method\"},\"request\":{\"customLabel\":\"Request\"},\"response_size\":{\"customLabel\":\"Response Size\"},\"status_code\":{\"customLabel\":\"Status Code\"},\"timestamp\":{\"customLabel\":\"Timestamp\"},\"user_agent\":{\"customLabel\":\"User Agent\"}}",
#           "title": "nginx-index-*",
#           "sourceFilters": "[]",
#           "fields": "[]",
#           "fieldFormatMap": "{}",
#           "runtimeFieldMap": "{}",
#           "name": "My Nginx Data View",
#           "allowHidden": false
#         },
#         "references": [],
#         "managed": false,
#         "coreMigrationVersion": "8.8.0",
#         "typeMigrationVersion": "8.0.0"
#       },
#       {
#         "id": "nginx-data",
#         "type": "index-pattern",
#         "namespaces": [
#           "default"
#         ],
#         "updated_at": "2024-08-14T11:04:58.271Z",
#         "created_at": "2024-08-14T09:04:10.899Z",
#         "version": "WzExNSwxXQ==",
#         "attributes": {
#           "allowHidden": false,
#           "fieldAttrs": "{\"program\":{\"customLabel\":\"Program\"},\"timestamp\":{\"customLabel\":\"Timestamp\"},\"syslog_message\":{\"customLabel\":\"Message\"}}",
#           "fieldFormatMap": "{}",
#           "fields": "[]",
#           "name": "My Filebeat Data View",
#           "runtimeFieldMap": "{}",
#           "sourceFilters": "[]",
#           "title": "filebeat-index-*"
#         },
#         "references": [],
#         "managed": false,
#         "coreMigrationVersion": "8.8.0",
#         "typeMigrationVersion": "8.0.0"
#       }
#     ]
#   }
#   ')
# fi

# if [[ "$response" == *"\"attributes\":{\"title\":\"Bill Dashboard\""* ]]; then
#   echo -e "${COLOR_GREEN}All Dashboards creation completed.${COLOR_RESET}"
# else
#   echo -e "${COLOR_RED}\nIssue with Dashboards creation.${COLOR_RESET}"
#   echo -e "$response"
#   exit 1;
# fi
