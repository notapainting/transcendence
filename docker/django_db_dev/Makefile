
CMP = docker-compose --file compose.yml --env-file env.example

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

logs:
	${CMP} logs 

	# hostname: bd