
CMP = docker-compose --file compose.yml --env-file apps/auth_service/env.example

all :	up

build :	
	${CMP} build

up :	build
	${CMP} up -d

down :
	${CMP} down 

clear:
	${CMP} down --rmi all -v --remove-orphans

ps:
	${CMP} ps

config:
	${CMP} config


logs:
	${CMP} logs 