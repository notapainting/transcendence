
# Transcendence
Our last common core projects at 42 school


## Demo
![gif of the site landing page](https://raw.githubusercontent.com/notapainting/transcendence/main/demo.gif)

## Features

#### Web UI
- A woody Pong game
- Play locally or with your friend all over the internet !!!
- Tournament up to 16 players! 
- Magnicent transition between each page
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

This will generate .env file based on template in conf/, please provide your own API key and change the default value of secrets keys, users, passwords


## Deployment
To deploy this project run

```bash
    make up-fg
```

## Module Documentations
[Chat](https://github.com/notapainting/transcendence/blob/main/apps/chat)
[Auth](https://github.com/notapainting/transcendence/blob/main/apps/chat)
[Blockchain](https://github.com/notapainting/transcendence/blob/main/apps/chat)
[User Managment](https://github.com/notapainting/transcendence/blob/main/apps/chat)


## Authors
- [@Louisa4124](https://www.github.com/Louisa4124)
- [@Bilel Lakehal](https://www.github.com/BilelLk)
- [@ikaismou](https://www.github.com/islemk69)
- [@titirex](https://www.github.com/titi-rex)
