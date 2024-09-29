# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: tlegrand <tlegrand@student.42lyon.fr>      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/03/10 21:52:05 by tlegrand          #+#    #+#              #
#    Updated: 2024/09/29 21:52:47 by tlegrand         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

-include conf/var.mk


#========#	general rule	#========#
.PHONY: all re init init-fg

all:	up-fg

fclean:
	@script/docker-full-clear.sh

re:	fclean up-fg

init: ${ENV_FILE} 
	@mkdir -p certs


#========#	build rule	#========#
.PHONY: build env-create env-clear mode-dev mode-prod vmmax

build:
	${CMP} build

env-create: ${ENV_FILE}

env-clear:
	@rm -f ${ENV_FILE}
	@echo "Delete old .env files.."

${DIR_ENV_FILE}%.env:	${DIR_ENV_FILE}%.template
	@cp $< $@
	@echo "Generate new  $@ file!"

UNAME_S := $(shell uname -s)

mode-dev:
ifeq ($(UNAME_S), Linux)
	@sed -i 's/MODE=prod/MODE=dev/g' conf/var.mk
else ifeq ($(UNAME_S), Darwin)
	@sed -i '' 's/MODE=prod/MODE=dev/g' conf/var.mk
endif
	@echo "Switched to DEV mode, please build and run accordingly."

mode-prod:
ifeq ($(UNAME_S), Linux)
	@sed -i 's/MODE=dev/MODE=prod/g' conf/var.mk
else ifeq ($(UNAME_S), Darwin)
	@sed -i '' 's/MODE=dev/MODE=prod/g' conf/var.mk
endif
	@echo "Switched to PROD mode, please build and run accordingly."


vmmax:
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo sysctl -w vm.max_map_count=262144; \
	else \
		echo "Skipping vm.max_map_count setting on non-Linux system"; \
	fi


#========#	start/stop rule	#========#
.PHONY: up up-fg down clear

up:		${ENV_FILE}
	${CMP} up --build -d

up-fg:	${ENV_FILE}
	${CMP} up --build

down:
	${CMP} down 

up-nl:
	${CMP_NL} up --build

down-nl:
	${CMP_NL} down

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

gen-keys:
	@openssl rand -base64 32
	@openssl rand -base64 32
	@openssl rand -base64 32
	@openssl rand -base64 32
	@openssl rand -base64 32

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

