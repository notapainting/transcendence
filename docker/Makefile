
all :	up

build :
	docker-compose build

up :
	docker-compose up -d

down :
	docker-compose down 

clear:
	docker-compose down --rmi all -v --remove-orphans

ps:
	docker-compose ps

enter:
	docker-compose exec django bash