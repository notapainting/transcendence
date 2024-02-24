
CMP = docker-compose --env-file apps/auth_service/env.example \
	--file compose.yml \
	--file compose/compose.auth_service.yml \
	--file compose/compose.test.yml 

all :	up

build :	
	${CMP} build

up :	mdir build
	${CMP} up -d

down :
	${CMP} down 

clear:
	${CMP} down -v --remove-orphans

ps:
	${CMP} ps

config:
	${CMP} config
	# make -C apps/auth_service/ config

mdir:
	mkdir -p /logs

logs:
	${CMP} logs 

.PHONY: logs all build up down clear ps config mdir

# creeate /logs
# add /logs volume to compose
#  change docker file 
# make prod dockerfile
