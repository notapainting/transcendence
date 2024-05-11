ENV_FILE		=	.env

include .env

DOCKER_FILE =	docker-compose.yml
COMPOSE		=	docker compose
COMPOSE_F	=	docker compose -f
STOP		=	docker compose stop
RM			=	docker compose rm -f
RM_IMG		=	docker rmi
VOLUME		=	docker volume
NETWORK		=	docker network
SYSTEM		=	docker system

all:
	$(COMPOSE_F) $(DOCKER_FILE) --env-file $(ENV_FILE) up -d --build

prune:
	- $(STOP) $$(docker compose ps -qa)
	- $(RM) $$(docker compose ps -qa)
	- $(SYSTEM) prune -af
	- $(VOLUME) prune -af

down:
	$(COMPOSE) down


kill:
	$(COMPOSE) kill

restart:
	$(COMPOSE) restart

elasticsearch:
	$(COMPOSE) up -d elasticsearch
	$(COMPOSE_F) $(DOCKER_FILE) exec elasticsearch sh

logstash:
	$(COMPOSE) up -d logstash
	$(COMPOSE_F) $(DOCKER_FILE) exec logstash /bin/bash

kibana:
	$(COMPOSE) up -d kibana
	$(COMPOSE_F) $(DOCKER_FILE) exec kibana bash