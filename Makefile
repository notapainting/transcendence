# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: tlegrand <tlegrand@student.42lyon.fr>      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/03/10 21:52:05 by tlegrand          #+#    #+#              #
#    Updated: 2024/08/18 19:59:47 by tlegrand         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

-include conf/Makefile.var


#========#	general rule	#========#
.PHONY: all re build start up down clear top ps config logs reload proxy chat game auth user dev prod

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
env-create: ${ENV_FILE}
	

env-clear:
	rm -f ${ENV_FILE}
	echo "Delete old .env files.."


${DIR_ENV_FILE}%.env:	${DIR_ENV_FILE}%.template
	@cp $< $@
	@echo "Generate new  $@ file!"

config:
	${CMP} config

ps:
	${CMP} ps

top:
	${CMP} top

reload:
	docker container restart proxy

mode-dev:	${ENV_FILE}
	@sed -i 's/MODE=prod/MODE=dev/g' conf/main.env
	@echo "Switch to DEV mode, please build and run accordly"

mode-prod:	${ENV_FILE}
	@sed -i 's/MODE=dev/MODE=prod/g' conf/main.env
	@echo "Switch to PROD mode, please build and run accordly"


#========#	container access	#========#
proxy:
	docker exec -it proxy sh

auth:
	docker exec -it auth sh

user:
	docker exec -it user sh

game:
	docker exec -it game sh

chat:
	docker exec -it chat sh

