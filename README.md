# Offline Transcriber

This project is a simple web interface for creating subtitles from audio or video files. It runs entirely offline using the Whisper speech recognition model and Resemblyzer for basic speaker diarization.

## Features

- Works with common audio and video formats
- Automatically detects language or allows manual selection
- Generates `.srt` or `.ass` subtitle files with speaker tags
- Requires no API keys or external services

## Installation

1. Install [ffmpeg](https://ffmpeg.org/) so the app can convert your media files:
   - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - On macOS with Homebrew: `brew install ffmpeg`
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the transcriber with:

```bash
python transcriber_app.py
```

A browser window will open where you can upload audio or video, pick a language (or leave "Auto"), choose the subtitle format, and download the resulting file.
