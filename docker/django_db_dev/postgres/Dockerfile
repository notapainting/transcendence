FROM postgres:15-bookworm

ARG PORT
ARG PGDIR 

# RUN export PGDATA=${PGDIR}
RUN echo >> ${PGDIR}/postgresql.conf "port = "${PORT}
COPY pg_hba.conf ${PGDIR}/pg_hba.conf

USER postgres
RUN export PGDATA=${PGDIR}

USER postgres
RUN /usr/lib/postgresql/15/bin/pg_ctl reload

EXPOSE ${PORT}

# from debian:bookworm-slim
# apt update -y && apt upgrade -y
# apt install -y vim curl git man less systemctl postgresql-15 postgresql-contrib-15

# bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"
# conf
# pg_hba.conf -> auth 
# e PGDATA=/var/lib/postgresql/data/pgdata
# /usr/lib/postgresql/15/bin/pg_ctl

# pg_ctl -> 
# postgres@6139b07c1525:~$ /usr/lib/postgresql/15/bin/pg_ctl --help
# pg_ctl is a utility to initialize, start, stop, or control a PostgreSQL server.

# Usage:
#   pg_ctl init[db]   [-D DATADIR] [-s] [-o OPTIONS]
#   pg_ctl start      [-D DATADIR] [-l FILENAME] [-W] [-t SECS] [-s]
#                     [-o OPTIONS] [-p PATH] [-c]
#   pg_ctl stop       [-D DATADIR] [-m SHUTDOWN-MODE] [-W] [-t SECS] [-s]
#   pg_ctl restart    [-D DATADIR] [-m SHUTDOWN-MODE] [-W] [-t SECS] [-s]
#                     [-o OPTIONS] [-c]
#   pg_ctl reload     [-D DATADIR] [-s]
#   pg_ctl status     [-D DATADIR]
#   pg_ctl promote    [-D DATADIR] [-W] [-t SECS] [-s]
#   pg_ctl logrotate  [-D DATADIR] [-s]
#   pg_ctl kill       SIGNALNAME PID

# Common options:
#   -D, --pgdata=DATADIR   location of the database storage area
#   -s, --silent           only print errors, no informational messages
#   -t, --timeout=SECS     seconds to wait when using -w option
#   -V, --version          output version information, then exit
#   -w, --wait             wait until operation completes (default)
#   -W, --no-wait          do not wait until operation completes
#   -?, --help             show this help, then exit
# If the -D option is omitted, the environment variable PGDATA is used.

# Options for start or restart:
#   -c, --core-files       allow postgres to produce core files
#   -l, --log=FILENAME     write (or append) server log to FILENAME
#   -o, --options=OPTIONS  command line options to pass to postgres
#                          (PostgreSQL server executable) or initdb
#   -p PATH-TO-POSTGRES    normally not necessary

# Options for stop or restart:
#   -m, --mode=MODE        MODE can be "smart", "fast", or "immediate"

# Shutdown modes are:
#   smart       quit after all clients have disconnected
#   fast        quit directly, with proper shutdown (default)
#   immediate   quit without complete shutdown; will lead to recovery on restart

# Allowed signal names for kill:
#   ABRT HUP INT KILL QUIT TERM USR1 USR2
