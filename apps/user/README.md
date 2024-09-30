# User Management Microservice

This microservice handles the user-related operations such as user creation, information retrieval, updates, and fetching user match history. It is built using Django REST Framework and serves as part of the broader **ft_transcendence** project.

## Features

- **User Registration**: Allows new users to sign up for the application.
- **Retrieve User Information**: Get details about a specific user.
- **Update User Information**: Update client-related information.
- **Fetch All Users**: Retrieve information about all registered users.
- **User Match History**: Retrieve the match history for a specific user.

## Endpoints

### Public Endpoints

These endpoints are accessible directly and do not require passing through the authentication service:

- **`GET /user/users_info/`**: Fetch information about all registered users.
- **`GET /user/match_history/<username>/`**: Fetch the match history for a given user.

### Private Endpoints

These endpoints require prior authentication and are only accessible via the authentication service, which will make the requests to the user management service:

- **`POST /signup/`**: Register a new user.
- **`GET /getuserinfo/`**: Retrieve the current user's information.
- **`PUT /update_client/`**: Update the current user's client information.
