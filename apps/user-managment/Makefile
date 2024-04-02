
CMP = docker compose --file compose.dev.yml --env-file app.env.example


all:	up

build:
	${CMP} build

up:	volume build
	${CMP} up -d

down:
	${CMP} down 

clear:
	${CMP} down --rmi all -v --remove-orphans

ps:
	${CMP} ps

config:
	${CMP} config

enter:
	${CMP} exec django bash

volume:
	mkdir -p django/src/


logs:
	${CMP} logs 
