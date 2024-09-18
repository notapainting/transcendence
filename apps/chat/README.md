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


## API Reference

### API HTTP

`<format:thing>` is optionnal

All endpoint should end by '/'

#### User Endpoint

Endpoint for all `User`-related operation

```http
  /api/v1/users/<name>/
```

| Method    | Parameter| Payload | Return Code | Description                |
| :-------- | :------- |:------- | :---------- | :------------------------- |
| `POST`    | `no`     | `name` [¹]()  | `201`, `400`| Create `User`  |
| `GET`     | `no`     | `no`    | `200`, `404`| Retrieve `User` data or list all `User` |
| `PATCH`   | `yes`    | `new_name`, `contact` [²]() | `200`, `400`, `404`| Update `User` data |
| `DELETE`  | `yes`    | `no`    | `200`, `404`| Delete `User` |

#### Group Endpoint

Endpoint for all `Group`-related operation

```http
  /api/v1/groups/<uuid:id>/
```

| Method    | Parameter| Payload | Return Code | Description                |
| :-------- | :------- |:------- | :---------- | :------------------------- |
| `POST`    | `no`     | `name, author, admins, members, restricts` [³]() | `201`, `400`| Create `User`  |
| `GET`     | `no`     | `no`    | `200`, `404`| Retrieve `Group` data or list all `Group` |
| `PATCH`   | `yes`    | `name, admins, members, restricts, remove` [⁴]() | `200`, `400`, `404`| Update `Group` data |
| `DELETE`  | `yes`    | `no`    | `200`, `404`| Delete `Group` |




```
1
{
    "name":"borys"
}


2
{
    "new_name":"borys",
}
    or
{
    "contact":
    {
        "author":"arlan",
        "name":"astra",
        "operation":"contact/block/invit/remove"
    }
}


3
{
    "name": "Stellaron Hunter Chatgroup's",
    "author": "luciole",
    "admins":["sam"],
    "members": ["xueyi", "acheron"],
    "restricts": []
}

```