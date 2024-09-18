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

-include conf/var.mk


#========#	general rule	#========#
.PHONY: all re init init-fg    

all:	init-fg

re:	clear start

init: ${ENV_FILE} vmmax
	${CMP} up --build -d 

init-fg: ${ENV_FILE} vmmax
	${CMP} up --build


#========#	build rule	#========#
.PHONY: build env-create env-clear mode-dev mode-prod vmmax
build:
	${CMP} build

env-create: ${ENV_FILE}

env-clear:
	@rm -f ${ENV_FILE}
	echo "Delete old .env files.."

${DIR_ENV_FILE}%.env:	${DIR_ENV_FILE}%.template
	@cp $< $@
	@echo "Generate new  $@ file!"

mode-dev:
	@sed -i 's/MODE=prod/MODE=dev/g' conf/Makefile.var
	@echo "Switch to DEV mode, please build and run accordly"

mode-prod:
	@sed -i 's/MODE=dev/MODE=prod/g' conf/Makefile.var
	@echo "Switch to PROD mode, please build and run accordly"

vmmax:
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo sysctl -w vm.max_map_count=262144; \
	else \
		echo "Skipping vm.max_map_count setting on non-Linux system"; \
	fi


#========#	start/stop rule	#========#
.PHONY: up up-fg down clear
up:		${ENV_FILE}
	${CMP} up -d

up-fg:	${ENV_FILE}
	${CMP} up 

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

