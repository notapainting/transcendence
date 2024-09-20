# Chat 

## Tech Stack

 Django 5.0.2, Django Channels 4.0.0, Django REST Framework 3.14.0, Redis 7.2.4, Postgres 16

## Architecture

The chat is mainly composed of 3 objects : `User`, `Group`, `Message`, and relation between them. 

A `User` can invite another `User`, if this one accept, they both become `Contact`. Alternatively, one can block another `User` so they cannot send `Message`.

The API provide a way to retrieve `User` presence in `Contact` list, currently there is 3 options implemented in backend :`disconnected, online, afk`.

A `Group` can be used as a private conversation between two `User` or a group conv with multiple members and a custom name. Each members has a role associated with certains permissions : `owner, admin, member, restrict`. A `Group` store information about the last message read of a `User`

A `Message` has a `User` author, a `Group` related, a `date` (set automatically), a `body` and optionnaly can respond to another `Message`


## Tech Stack

 Django 5.0.2, Django Channels 4.0.0, Django REST Framework 3.14.0, Redis 7.2.4, Postgres 16

## Architecture

The chat is mainly composed of 3 objects : `User`, `Group`, `Message`, and relation between them. 

A `User` can invite another `User`, if this one accept, they both become `Contact`. Alternatively, one can block another `User` so they cannot send `Message`.

The API provide a way to retrieve `User` presence in `Contact` list, currently there is 3 options implemented in backend :`disconnected, online, afk`.

A `Group` can be used as a private conversation between two `User` or a group conv with multiple members and a custom name. Each members has a role associated with certains permissions : `owner, admin, member, restrict`. A `Group` store information about the last message read of a `User`

A `Message` has a `User` author, a `Group` related, a `date` (set automatically), a `body` and optionnaly can respond to another `Message`

![schema of database architecture](https://raw.githubusercontent.com/notapainting/transcendence/main/chat_db_schema_short.png)


## API Reference

### API HTTP

`<format:thing>` is optionnal

All endpoint should end by '/'

#### User Endpoint

Endpoint for all `User`-related operation

```http
  /api/v1/users/<name>/
```

| Method    | Parameter Required | Payload Expected | Return Code | Description                |
| :-------- | :-------  |:------- | :---------- | :------------------------- |
| `POST`    | `no`      | `name` [¹](#1)  | `201`, `400`| Create `User`  |
| `GET`     | `no`      | `no`    | `200`, `404`| Retrieve `User` data or list all `User` |
| `PATCH`   | `yes`     | `new_name`, `contact` [²](#2) | `200`, `400`, `404`| Update `User` data |
| `DELETE`  | `yes`     | `no`    | `200`, `404`| Delete `User` |

#### Group Endpoint

Endpoint for all `Group`-related operation

```http
  /api/v1/groups/<uuid:id>/
```

| Method    | Parameter Required | Payload Expected | Return Code | Description                |
| :-------- | :-------  |:------- | :---------- | :------------------------- |
| `POST`    | `no`      | `name, author, admins, members, restricts` [³](#3) | `201`, `400`| Create `User`  |
| `GET`     | `no`      | `no`    | `200`, `404`| Retrieve `Group` data or list all `Group` |
| `PATCH`   | `yes`     | `name, admins, members, restricts, remove` [⁴](#4) | `200`, `400`, `404`| Update `Group` data |
| `DELETE`  | `yes`     | `no`    | `200`, `404`| Delete `Group` |


#### Message Endpoint

Endpoint for all `Message`-related operation

```http
  /api/v1/messages/<uuid:id>/
```

| Method    | Parameter Required | Payload Expected | Return Code | Description                |
| :-------- | :-------  |:------- | :---------- | :------------------------- |
| `POST`    | `no`      | `name, author, admins, members, restricts` [⁵](#5) | `201`, `400`, `404`| Create `Message` related to a `Group` and a author `User`  |
| `GET`     | `yes`      | `no`    | `200`, `400`, `404`| Retrieve `Message` data with id |
| `PATCH`   | `yes`     | `name, admins, members, restricts, remove` [⁵](#5) | `200`, `400`, `404`| Update `Message` data |
| `DELETE`  | `yes`     | `no`    | `200`, `404`| Delete `Message` |


#### Query Fields

All `GET` can be filtered with passing `fields` inside query string

example :

```http
GET /api/v1/groups/bff768c5-de7c-42e7-ac2b-b4dd2760ffc/?fields=name+id

```
will return :

```json
{
	"id":"bff768c5-de7c-42e7-ac2b-b4dd2760ffc",
	"name":"Secret Special Group",
}
```

#### Payload Example

##### 1
```json
{
    "name":"borys"
}
```

##### 2
```json
{
    "new_name":"borys",
}
```
or
```json
{
    "contact":
    {
        "author":"arlan",
        "name":"astra",
        "operation":"contact/block/invit/remove"
    }
}
```

##### 3
```json
{
    "name": "Stellaron Hunter Chatgroup's",
    "author": "luciole",
    "admins":["sam"],
    "members": ["xueyi", "acheron"],
    "restricts": []
}
```

##### 4
```json
{
	"name": "New Super Cool New Name",
	"admins":["fuxuan"],
	"members": ["xueyi", "acheron"],
	"restricts": [], 
	"remove":["sam"]
}
```


##### 5
```json
{
	"author":"luciole",
	"group": "bff768c5-de7c-42e7-ac2b-b4dd2760ffc4",
	"respond_to": "",
	"date":"2024-05-12T10:29:16.000949",
	"body": "message in the past !"
}
```

