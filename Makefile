
CMP = docker compose --env-file env.dev \
	--file compose.yml \
	--file compose/compose.app.yml \
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

mdir:
	mkdir -p \
		logs \
		apps/django_db_dev/django/src \
		apps/django_db_dev/postgres/data

deldb:
	rm -rf \
		apps/django_db_dev/django/src \
		apps/django_db_dev/postgres/data

logs:
	${CMP} logs 

re:	clear up

.PHONY: logs all build up down clear ps config mdir re

# creeate /logs
# add /logs volume to compose
#  change docker file 
# make prod dockerfile
