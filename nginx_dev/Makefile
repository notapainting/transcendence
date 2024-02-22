
CMP = docker compose --file compose.yml

all :	up

build :	
	${CMP} build

up :
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
	${CMP} exec nginx bash

re:	clear up