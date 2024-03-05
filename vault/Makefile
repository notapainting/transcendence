
CMP = docker compose --env-file env.vault \
	--file compose.vault.yml 

all :	up

build :	
	${CMP} build

run:
	docker run --rm --name vault -v ./vault/conf:/vault/config -p 8200:8200 --cap-add=IPC_LOCK hashicorp/vault server

enter: 
	docker exec -it vault sh

up :	build
	${CMP} up -d

down :
	${CMP} down 

clear:
	${CMP} down -v --remove-orphans

ps:
	${CMP} ps

config:
	${CMP} config


logs:
	${CMP} logs 

.PHONY: logs all build up down clear ps config mdir

# creeate /logs
# add /logs volume to compose
#  change docker file 
# make prod dockerfile
