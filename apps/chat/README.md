# Chat 

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

### API REST

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

## API Websocket

Handshake endpoint : `chat/`

Each message must be formated with a `type` key and `data` key

Client are not required to supply `date` and `author` fields, they are automatically set in backend

### Two send/receive event

Client to server or server to client event


#### Message

`message.text`

Send or receive a simple message inside an already existing `Group`

`respond_to` can be empty

```json
{
	"type":"message.text",
	"data":
	{
		"author":"Herta",
		"to":"755b83ae-0cb9-461c-8639-b55ec589a6a5",
		"body":"go get me a coffee",
		"respond_to": "45648efsef-0cb9-461c-8639-b48ec589a6a5",
		"date":"2024-05-12T10:29:16.000949"
	}
}
```


#### First Message

`message.first`

Initiate a private conversation with another `User` if there wasn't already a private `Group`


```json
{
	"type":"message.first",
	"data":
	{
		"author":"Stelle",
		"target":"Yanqing",
		"body":"Hello, did you see my baseball-style sword?"
	}
}
```
#### Message history

`message.fetch`

Request last 20 message older than `date`

```json
{
	"type":"message.fetch",
	"data":
	{
		"author":"SilverWolfe",
		"date":"2024-05-15T12:02:01.005411"
	}
}
```

#### Update User Status

`status.update`

Update the `User` status

`status` can be `online`, `afk` or `disconnected`

```json
{
	"type":"status.update",
	"data":
	{
		"author":"Kafka",
		"status":"afk"
	}
}
```

#### Modify contact

`contact.update`

Do `operation` on relation from `author` to `target`

`operation` can be : 

`contact`: add `target` to contact list, (actualy, perform similar operation that `invitation`)

`invitation`: send a contact invitation to `target`, if `target` has already send an `invitation`, resolve it and add `target` has a contact insteed

`deny` : refuse a contact invitation

`blocked` : block `target`

`remove` : remove current relation


```json
{
	"type":"contact.update",
	"data":
	{
		"author":"Qingque",
		"name":"FuXuan",
		"operation":"block"
	}
}
```

#### Create a group conversation

`group.create`

Create a `Group` for multiple users

`admins`, `members`, `restricts` can be empty list


```json
{
	"type":"group.create",
	"data":
	{
		"author":"Elio",
		"name":"Stellaron Hunter Chatgroup's",
		"admins":["Kafka"],
		"members":["Sam", "SilverWolf", "Stelle"],
		"restricts":["Blade", "FuXuan"],
	}
}
```

#### Update group information

`group.update`

Update a group: change name, remove/add members, or change members role


```json
{
	"type":"group.update",
	"data":
	{
		"author":"Elio",
		"id":"755b83ae-0cb9-461c-8639-b55ec589a6a5",
		"name":"Stellaron Hunter Chatgroup's",
		"admins":["Kafka"],
		"members":["Sam", "SilverWolf", "Stelle"],
		"restricts":["Blade"],
		"remove":["FuXuan"],
	}
}
```

#### Quit a group

`group.quit`

Quit a group

```json
{
	"type":"group.quit",
	"data":
	{
		"author":"SilverWolf",
		"id":"755b83ae-0cb9-461c-8639-b55ec589a6a5"
	}
}
```

### Client side receive event

Bakcend to client only event

#### Group Summary 

`group.summary`

List of all groups where user is inside

```json
{
	"type":"group.summary",
	"data":
		{
			[
				"id":"",
				"name":"",
				"members":[],
				"admins":[],
				"restricts":[],
				"messages":[],
				"last_read":""
			],
			[
				...
			]
		}
}
```

#### Contact Summary

`contact.summary`

List of all `User` relation

`relation` can be: `contact`, `blocked` or `invitation`

```json
{
	"type":"contact.summary",
	"data":
	{
		[
			"name":"Gepard",
			"relation":"contact"
		],
		[
			"name":"Lynx",
			"relation":"contact"
		],
		[
			...
		]
	}
}
```
