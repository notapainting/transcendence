# Authentication Microservice

This microservice handles user authentication, including registration, login, password reset, email verification, two-factor authentication, and OAuth integration. It is part of the broader `ft_transcendence` project, and interacts with the other microservices for user authentication and session management.

## Table of Contents

- [Routes](#routes)
- [Authentication Flow](#authentication-flow)
- [JWT Tokens](#jwt-tokens)
- [OAuth Integration](#oauth-integration)
- [Two-Factor Authentication](#two-factor-authentication)
- [Installation and Setup](#installation-and-setup)
- [Environment Variables](#environment-variables)

## Routes

### Public Routes

- **`/auth/signup/`**  
  Allows a new user to create an account.  
  **Method**: POST

- **`/auth/token/`**  
  Obtain JWT tokens (access and refresh) upon successful login.  
  **Method**: POST

- **`/auth/token/refresh/`**  
  Refreshes the access token using a valid refresh token.  
  **Method**: POST

- **`/auth/verify-email/<uidb64>/<token>/`**  
  Verifies the user's email after registration.  
  **Method**: GET

- **`/auth/reset_password/`**  
  Sends an email to the user to reset the password.  
  **Method**: POST

- **`/auth/password_reset_confirm/<uidb64>/<token>/`**  
  Resets the user password using the token sent via email.  
  **Method**: POST

### Protected Routes

- **`/auth/activate2FA/`**  
  Activates two-factor authentication (2FA) for the user.  
  **Method**: POST

- **`/auth/confirm2FA/`**  
  Confirms the 2FA code to complete the 2FA setup.  
  **Method**: POST

- **`/auth/validate_token/`**  
  Validates the current JWT token.  
  **Method**: POST

- **`/auth/update_client/`**  
  Updates the user profile information (excluding profile picture).  
  **Method**: PUT

- **`/auth/update_picture/`**  
  Updates the user profile picture.  
  **Method**: PUT

- **`/auth/get_pers_infos/`**  
  Retrieves the user's personal information.  
  **Method**: GET

- **`/auth/logout/`**  
  Logs the user out and invalidates the JWT token.  
  **Method**: POST

## Authentication Flow

1. **Sign Up**: Users register with an email and password.
2. **Email Verification**: A verification email is sent to the user's email address, which contains a token to verify their email.
3. **Login**: Once verified, the user can log in and receive a JWT access token and refresh token.
4. **Token Refresh**: Users can refresh their access token using the refresh token to stay authenticated.

## JWT Tokens

This microservice uses JSON Web Tokens (JWT) for stateless authentication. The access token is short-lived and used for authorization, while the refresh token is long-lived and used to renew the access token.

- **Access Token**: Used to authenticate API requests.
- **Refresh Token**: Used to request a new access token once the previous one has expired.

Both tokens are stored in HttpOnly cookies to improve security.

## OAuth Integration

The system supports OAuth2 login with the **42** authentication system:
- **`/auth/authenticate_with_42/`**: Initiates the OAuth process.
- **`/auth/Oauth/`**: Handles the callback from **42** and logs in the user or registers them if it's their first time.

## Two-Factor Authentication (2FA)

For additional security, users can enable two-factor authentication (2FA):
- After activating 2FA via `/auth/activate2FA/`, users will be required to confirm the code sent to their device via `/auth/confirm2FA/`.

## Environment Variables

The following environment variables are required for the service to run properly:

- SECRET_KEY: Django's secret key for cryptographic signing.
- EMAIL_HOST_USER: The email address used to send verification and password reset emails.
- EMAIL_HOST_PASSWORD: The password for the email address.
- DJANGO_SECRET_KEY: Secret key for encoding JWT tokens.
- UID: OAuth Client ID for 42 integration.
- SECRET_KEY: OAuth Client Secret for 42 integration.
