#========#    general    #========#
MAKEFLAGS   +=   -s
MODE=dev


#========#	env 	#========#
DIR_ENV_FILE        =   conf/
LST_TEMPLATE_FILE   =   auth.template chat.template game.template proxy.template user.template blockchain.template main.template
TEMPLATE_FILE       =   ${addprefix ${DIR_ENV_FILE}, ${LST_TEMPLATE_FILE}}
ENV_FILE            =   ${TEMPLATE_FILE:.template=.env}


#========#	compose	#========#
DIR_CMP		=	compose/
RAW_FILE	=	.auth.yml .user.yml .chat.yml .game.yml .blockchain.yml
OK_FILE     =   compose.proxy.yml compose.elk.yml
LST_FILE    =   ${addprefix ${MODE}, ${RAW_FILE}} ${OK_FILE}


FILE	=	${addprefix --file , ${addprefix ${DIR_CMP}, ${LST_FILE}}}


BASE    =    docker compose \
				--parallel -1\
                --env-file conf/main.env \
                --file compose.network.yml 

CMP        =    ${BASE} ${FILE}


#========#    colors    #========#
BLACK       =    \033[0;30m
RED         =    \033[0;31m
GREEN       =    \033[0;32m
YELLOW      =    \033[0;33m
BLUE        =    \033[0;34m
PURPLE      =    \033[0;35m
CYAN        =    \033[0;36m
GRAY_LIGHT  =    \033[0;37m
GRAY_DARK   =    \033[1;30m
RED_LIGHT   =    \033[1;31m
GREEN_LIGHT =    \033[1;32m
YELLOW_L    =    \033[1;33m
BLUE_LIGHT  =    \033[1;34m
VIOLET      =    \033[1;35m
CYAN        =    \033[1;36m
WHITE       =    \033[1;37m
END         =    \033[0m
BOLD        =    \033[1m
FAINT       =    \033[2m
ITALIC      =    \033[3m
UNDERLINE   =    \033[4m
BLINK_SLOW  =    \033[5m
BLINK_FAST  =    \033[6m
BLINK_OFF   =    \033[25m
REV_V       =    \033[7m
CONCEAL     =    \033[8m
CONCEAL_OFF =    \033[28m
CROSS_OUT   =    \033[9m
CROSS_OUT_O =    \033[29m
ERASE       =    \033[2K
RERASE      =    \r\033[2K