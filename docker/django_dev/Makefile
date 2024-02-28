
CMP = docker compose --file compose.dev.yml --env-file app.env.example

all :	up

build :	
	${CMP} build

up :	volume
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