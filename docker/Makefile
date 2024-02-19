
all :	up

up :
	docker-compose up --build -d

down :
	docker-compose down --rmi all -v --remove-orphans

ps:
	docker-compose ps

enter:
	docker-compose exec django bash