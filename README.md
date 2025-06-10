# Multiplayer Snake Game

This demo allows multiple players to play a basic Snake game at the same time. Each player can register/login with an email and password and their best score is stored in a SQLite database.

## Setup

1. Install dependencies and start the server:

```bash
cd server
npm install
npm start
```

The server runs on port 3000.

2. Open `client/index.html` in your browser. Use the register/login form to authenticate, then play the game. The leaderboard will show top scores.
