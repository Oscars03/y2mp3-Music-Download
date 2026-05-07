# 🎵 y2mp3-Music-Download

A smart YouTube to MP3 downloader with a graphical user interface (GUI) built in Python.

Unlike standard downloaders, this tool uses a local AI (Llama 3.1 via Ollama) to automatically clean up messy YouTube titles (removing clutter like [Official MV], (Lyrics)) and formats them perfectly with proper metadata tagging.

## 🚧 Limitations & Restrictions (What it Can and Can't Do)

To set the right expectations, here is a clear breakdown of the tool's capabilities and current boundaries:

### ✅ What it CAN do:
* **Download Public & Unlisted Content:** Works seamlessly with standard YouTube videos and public/unlisted playlists.
* **Clean & Format Titles:** Automatically removes YouTube-specific clutter (e.g., `[Official MV]`, `(Lyrics)`, `4K`) and enforces a strict `Song - Artist` naming convention.
* **Smart Fallback:** If an artist's name is entirely missing from the video title, the tool intelligently extracts the YouTube Channel name and formats it as the artist.
* **Tag Files:** Embeds standard ID3 metadata (Title, Artist, Album) and the YouTube thumbnail as the cover art directly into the MP3 file.
* **Apply Hardcoded Rules:** Contains specific bypass rules to correctly identify tricky Thai indie bands (e.g., *Three Man Down*, *Only Monday*, *มนัสวีร์*, *LHAM SOMPHOL*).

### ❌ What it CANNOT do:
* **Bypass DRM or Other Platforms:** This tool is strictly a YouTube downloader. It does NOT support downloading from Spotify, Apple Music, Joox, or any DRM-protected streaming services.
* **Download Private/Members-Only Videos:** If a video requires a login, is set to Private, or is restricted to channel members, the tool cannot access it and will automatically skip it.
* **Fetch Official Studio Album Art:** The tool embeds the *YouTube video thumbnail* as the album cover. It does not scrape official high-resolution album covers from external music databases.
* **Run Instantly on Low-End Hardware:** Because the Llama 3.1 model runs *locally* on your machine via Ollama, the AI analysis speed depends entirely on your computer's CPU/GPU capabilities.
* **Guarantee 100% AI Perfection:** While the prompt is heavily optimized, 8B parameter models can still occasionally hallucinate on highly abstract or poorly named videos. (It is highly recommended to leave the **"Popup Confirm"** feature enabled for manual verification).

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
