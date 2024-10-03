
# Pong Game

Our 3D Pong game is a modern reimagining of the classic Pong game, developed using Three.js for 3D rendering on the client side and Django for back-end management. This version offers an immersive 3D gaming experience while retaining the simplicity and appeal of the original Pong.


## Features

- Smooth 3D rendering with Three.js
- Real-time multiplayer mode
- Scoring and leaderboard system
- Tournament system
  
## Tech Stack

**Client:** ThreeJS, HTML, CSS

**Server:** Django 5.0.2, Django Channels 4.0.0

![preview of the game](https://github.com/notapainting/transcendence/blob/main/img/doc/gamePreview.png)
## Game Modes

**Local Play (Offline)**: Enjoy the game without an internet connection, perfect for quick matches or practice sessions.

**Online Play**: Compete with players worldwide, leveraging our user management module for seamless online interactions.

## Controls

In Local mode, You can use `w/s` or `ArroyUp/Arroydown` to move the paddle on left and right side respectively. If you play online any of theses key will move your paddle


## Tournament System

We've implemented a comprehensive tournament system with the following features:
- Tournament Creation: Users can host tournaments, customizing various parameters:
    - Number of players (supports multiple players beyond the traditional 2-player setup)
    - Points required to win a match
    - Activation or deactivation of power-ups
- Invitation System: Tournament hosts can invite players through:
    - The tournament control panel
    - Direct invitations via the in-game chat system
## Power-ups

The game features a variety of power-ups that add an exciting layer of strategy and unpredictability to matches. Players can collect both bonuses and penalties throughout the game, which can significantly influence gameplay dynamics.

**Examples of Power-ups:**

- Size Change: Temporarily increases or decreases the size of a player's paddle, affecting their ability to hit the ball.
- Speed Reduction: Slows down the paddle's speed, making it harder to react and control during intense moments.
## Backend (Django)

- Manages user data, game states, and tournament logistics.
- Implements RESTful APIs for front-end communication.
- Handles real-time game synchronization for online play.
## Frontend (Three.js)

- Renders the 3D game environment.
- Manages local game logic for offline play.
- Communicates with the backend for online features.
This architecture allows for a scalable, feature-rich gaming experience that caters to both casual and competitive players. The combination of local and online play, along with the tournament and matchmaking systems, provides a diverse and engaging Pong 3D experience.
