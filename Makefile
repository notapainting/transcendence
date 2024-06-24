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


-waf-warn:
ifeq (${PROXY_FILE}, compose.proxy.yml)
	@printf "${RED_LIGHT}WARNING: WAF disabled !!!${END}\n"
endif

#========#	build rule	#========#
build: -waf-warn
	${CMP} build

waf:
	@sed -i'' 's/compose.proxy.yml/compose.proxy.waf.yml/g' Makefile.var
	@printf "${GREEN}${BOLD}WAF turn on :)\n${YELLOW}${ITALIC}please build image again${END}\n"

no-waf:
	@sed -i'' 's/compose.proxy.waf.yml/compose.proxy.yml/g' Makefile.var
	@printf "${RED}${BOLD}Warning WAF disabled!!!\n${YELLOW}${ITALIC}please build image again${END}\n"


#========#	start/stop rule	#========#
start: -waf-warn
	sudo sysctl -w vm.max_map_count=262144
	${CMP} up --build

clear:
	${CMP} down -v --remove-orphans --rmi all

up:	-waf-warn
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

enter:
	docker exec -it chat bash
