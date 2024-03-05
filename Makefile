
CMP = docker compose --env-file env.dev \
	--file compose.yml \
	--file vault/compose.vault.yml \
	--file compose/compose.app.yml 

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

.PHONY: logs all build up down clear ps config mdir

# creeate /logs
# add /logs volume to compose
#  change docker file 
# make prod dockerfile
