# Multiplayer Snake Game

This demo allows multiple players to play a basic Snake game at the same time. Each player can register/login with an email and password and their best score is stored in a SQLite database.

## Setup

1. Install dependencies and start the server:

```bash
cd server
npm install
npm start
```

Run the unit tests with:

```bash
npm test
```

The server runs on port 3000.

2. Open `client/index.html` in your browser. Use the register/login form to authenticate, then play the game. The leaderboard will show top scores.

## Transcriber App

`transcriber_app.py` is a standalone script that transcribes audio or video files and produces `.srt` subtitles with basic speaker diarization. It relies only on local models (Whisper and Resemblyzer) and runs entirely offline.

Run the app with:

```bash
pip install -r requirements.txt
python transcriber_app.py
```

A browser window will open allowing you to upload media files and download the generated subtitles.
