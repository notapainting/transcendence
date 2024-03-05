
CMP = docker compose --env-file env.dev \
	--file compose.yml \
	--file compose/compose.auth_service.yml \
	--file compose/compose.user_managment.yml

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

mdir:
	mkdir -p \
		logs \
		apps/game/django/src \
		apps/auth_service/src \
		apps/user_managment/django/src

logs:
	${CMP} logs 

.PHONY: logs all build up down clear ps config mdir

# creeate /logs
# add /logs volume to compose
#  change docker file 
# make prod dockerfile
