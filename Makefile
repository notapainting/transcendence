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
.PHONY: all re init init-bg    

all:	init

re:	clear start

init: ${ENV_FILE} vmmax build up-fg

init-bg: ${ENV_FILE} vmmax build up-bg
	

#========#	build rule	#========#
.PHONY: build env-create env-clear mode-dev mode-prod vmmax
build:
	${CMP} build

env-create: ${ENV_FILE}

env-clear:
	rm -f ${ENV_FILE}
	echo "Delete old .env files.."

${DIR_ENV_FILE}%.env:	${DIR_ENV_FILE}%.template
	@cp $< $@
	@echo "Generate new  $@ file!"

mode-dev:	${ENV_FILE}
	@sed -i 's/MODE=prod/MODE=dev/g' conf/Makefile.var
	@echo "Switch to DEV mode, please build and run accordly"

mode-prod:	${ENV_FILE}
	@sed -i 's/MODE=dev/MODE=prod/g' conf/Makefile.var
	@echo "Switch to PROD mode, please build and run accordly"

vmmax:
	sudo sysctl -w vm.max_map_count=262144


#========#	start/stop rule	#========#
.PHONY: up-fg up-bg down clear
up-fg:
	${CMP} up

up-bg:
	${CMP} up -d 

down:
	${CMP} down 

clear:
	${CMP} down -v --remove-orphans 


#========#	tools rule	#========#
.PHONY: config ps top mode
config:
	${CMP} config

ps:
	${CMP} ps

top:
	${CMP} top

mode:
	@echo "Mode is ${MODE}"


#========#	container access	#========#
.PHONY: reload proxy chat game auth user
reload:
	docker container restart proxy

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

