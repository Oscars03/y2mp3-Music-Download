# 🎵 y2mp3-Music-Download

A smart YouTube to MP3 downloader with a graphical user interface (GUI) built in Python.

Unlike standard downloaders, this tool uses a local AI (Llama 3.1 via Ollama) to automatically clean up messy YouTube titles (removing clutter like [Official MV], (Lyrics)) and formats them perfectly with proper metadata tagging.

---

## ✨ Features

- **GUI Interface**: Easy-to-use interface built with tkinter
- **Playlist Support**: Download single videos or entire YouTube playlists
- **AI-Powered Renaming**: Uses a local Llama 3.1 model to analyze YouTube titles and correctly extract track and artist names
- **Smart Fallbacks**: If a title lacks an artist, the tool automatically fetches the YouTube channel name and assigns it as the artist
- **Auto ID3 Tagging**: Automatically embeds cleaned Title, Artist, and Album metadata into MP3 files
- **Live Track Detection**: Automatically detects live performances and appends [Live] to the track name
- **Interactive vs. Auto Mode**: Choose to manually verify names or let it run unattended
- **Thai Indie Band Rules**: Hardcoded parsing rules to prevent AI hallucination for specific band names

---

## 📁 File Overview

| File | Purpose |
|------|---------|
| `music_downloaderV2.py` | **Recommended** - All-in-one main application with downloading, AI renaming, and ID3 tagging |
| `music_downloader.py` | Legacy/basic version of the downloader |
| `metadata.py` | Standalone utility to fix ID3 tags for existing MP3 files |

---

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

### Required
- **Python 3.x**
- **FFmpeg** (Required by yt-dlp to extract audio)
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - Windows: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org)

### For AI Renaming Feature
- **Ollama & Llama 3.1**
  - Download from [ollama.com](https://ollama.com)
  - Pull the model: `ollama run llama3.1`
  - Ensure Ollama runs in the background before starting the app

---

## 🔧 Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Oscars03/y2mp3-Music-Download.git
cd y2mp3-Music-Download
```

2. **Install required Python libraries**:
```bash
pip install yt-dlp requests
```

3. **Install mutagen** (for ID3 tag editing):

   **Linux/Ubuntu** (Recommended):
   ```bash
   sudo apt install python3-mutagen
   ```

   **Windows/Mac**:
   ```bash
   pip install mutagen
   ```

---

## 💻 Usage

1. **Run the application**:
```bash
python3 music_downloaderV2.py
```

2. **Paste a YouTube URL** (video or playlist link)

3. **(Optional)** Set the number of songs to download (leave blank for entire playlist)

4. **Check/Uncheck "Popup Confirm"** to approve names manually or run automatically

5. **Click Start** - Files download to your system's default Music folder

---

## ⚠️ Important Notes

- The Llama 3.1 model must run locally on port `11434` (Ollama's default)
- Keep yt-dlp updated: `pip install --upgrade yt-dlp`
- Private or deleted videos in playlists are safely skipped
- Respect copyright laws and YouTube's terms of service when downloading

---

## 👤 Author

**Oscars03**

---

**Last Updated**: 2026-05-07
