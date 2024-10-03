
# Transcendence
Our last common core projects at 42 school

![Score](https://img.shields.io/badge/Score-125%2F100-brightgreen)
![Outstanding Project](https://img.shields.io/badge/Project-Outstanding-blue)

## Demo
![gif of the site landing page](https://raw.githubusercontent.com/notapainting/transcendence/main/img/doc/demo.gif)

## Features

#### Web UI
- A woody Pong game
- Play locally or with your friend all over the internet !!!
- Tournament up to 16 players! 
- Magnificent transition between each page
- Creating an account to access more features like : 
    - Match history
    - Live Chat
    - Add friend to contact list or block them
    - Change your profile picture
    - Logging with 42
    - Enabling 2FA for a protected account
    - Record match score on blokchain
- Single Page Application

#### Server
- Microservice Architecture with REST API
- ELK stack for log managment
- Backend protected by proxy with modSecurity WAF
- Deployement using docker container and docker compose
- Cross plateform
- Dev and prod docker image


## Tech Stack
**Frontend:** HTML, JS, CSS

**Backend:** Docker, Django, Redis, Postgres, Nginx, ModSecurity, Elasticsearch, Kibana, Logstash


## Installation
This project require `docker version 26.0.0`and `docker compose version 2.26.1`
You need to create .env for your container and augment `vm.max_map_count`[¹](https://access.redhat.com/solutions/99913) for ELk to work well, you can do it with :

```bash
  make init
```

This will generate .env file based on template in conf/, please provide your own API key, certificats and change the default value of secrets keys, users, passwords, etc

If you just want to test the project, certificats and defaults key, users, password are provided

## Deployment
To deploy this project run

```bash
    make up-fg
```

## Documentation

### Index

- [Chat](https://github.com/notapainting/transcendence/blob/main/apps/chat)
- [Authentification](https://github.com/notapainting/transcendence/blob/main/apps/auth)
- [Blockchain](https://github.com/notapainting/transcendence/blob/main/apps/blockchain)
- [User Managment](https://github.com/notapainting/transcendence/blob/main/apps/user)
- [Game](https://github.com/notapainting/transcendence/blob/main/apps/game)
- [Logging](https://github.com/notapainting/transcendence/blob/main/elk)


### Micro services architecture

![microservice architecture](https://raw.githubusercontent.com/notapainting/transcendence/main/img/doc/tr_ms_arch.png)


## Authors

- [@Louisa4124](https://www.github.com/Louisa4124)
- [@Bilel Lakehal](https://www.github.com/BilelLk)
- [@ikaismou](https://www.github.com/islemk69)
- [@titirex](https://www.github.com/titi-rex)
