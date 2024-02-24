
CMP = docker compose --file compose.yml --env-file env.example
PATH_DATA_DB = ${HOME}/goinfre/docker_volume/

all :	up

build :	
	${CMP} build

up :	volume build
	${CMP} up -d

down :
	${CMP} down 

clear:
	${CMP} down --rmi all -v --remove-orphans

ps:
	${CMP} ps

config:
	${CMP} config

enter:	up
	${CMP} exec django bash

volume:
	mkdir -p django/src/
	mkdir -p ${PATH_DATA_DB}db/

deldb:
	rm -rf ${PATH_DATA_DB}db/


logs:
	${CMP} logs 
