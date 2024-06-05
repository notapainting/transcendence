# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: tlegrand <tlegrand@student.42lyon.fr>      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/03/10 21:52:05 by tlegrand          #+#    #+#              #
#    Updated: 2024/05/13 20:14:09 by tlegrand         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

-include Makefile.var


#========#	general rule	#========#
.PHONY: all re build start up down clear top ps config logs enter

all:	start

re:	clear start


#========#	build rule	#========#
build:
	${CMP} build


#========#	start/stop rule	#========#
start:
	${CMP} up -d --build

clear:
	${CMP} down -v --remove-orphans --rmi all

up:
	${CMP} up -d 

down:
	${CMP} down 


#========#	tools rule	#========#
config:
	${CMP} config

ps:
	${CMP} ps

top:
	${CMP} top

logs:
	${CMP} logs 

reload:
	docker container restart proxy

proxy:
	docker exec -it proxy sh

auth:
	docker exec -it auth-service bash

user:
	docker exec -it user-managment bash

game:
	docker exec -it game bash

chat:
	docker exec -it chat bash