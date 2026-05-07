**y2mp3-Music-Download**
A smart YouTube to MP3 downloader with a graphical user interface (GUI) built in Python.

Unlike standard downloaders, this tool uses a local AI (Llama 3.1 via Ollama) to automatically clean up messy YouTube titles (removing clutter like [Official MV], (Lyrics)) and formats them perfectly into Song Name - Artist Name. It also automatically applies ID3 metadata tags (Title, Artist, Album) to the downloaded MP3 files.

**Features**
GUI Interface: Easy-to-use interface built with tkinter.

Playlist Support: Download single videos or entire YouTube playlists.

AI-Powered Renaming: Uses a local Llama 3.1 model to analyze YouTube titles and correctly extract the track and artist names.

Smart Fallbacks: If a title lacks an artist, the tool automatically fetches the YouTube Channel name and assigns it as the artist.

Auto ID3 Tagging: Automatically embeds the cleaned Title, Artist, and Album (taken from the Playlist name) directly into the MP3's metadata.

Live Track Detection: Automatically detects live performances and appends [Live] to the track name.

Interactive vs. Auto Mode: Choose to manually verify and edit the AI's suggested name via a popup dialog, or let it run completely unattended.

Thai Indie Band Rules: Contains hardcoded parsing rules to prevent AI hallucination for specific tricky band names (e.g., Three Man Down, Only Monday, มนัสวีร์, TaitosmitH).

**File Overview**
music_downloaderV2.py: The recommended, all-in-one main application. Handles downloading, AI renaming, and applies ID3 metadata immediately after the download finishes.

music_downloader.py: The legacy/basic version of the downloader.

metadata.py: A standalone utility tool. Scans a selected folder for MP3 files named as Song - Artist.mp3 and fixes their ID3 tags retroactively.

**Prerequisites**
Before running the application, ensure you have the following installed on your system:

Python 3.x

FFmpeg (Required by yt-dlp to extract audio)

Ubuntu/Debian: sudo apt install ffmpeg

Windows: Download via winget install ffmpeg or from the official site.

Ollama & Llama 3.1 (For the AI renaming feature)

Download Ollama from ollama.com

Pull the model: ollama run llama3.1 (Ensure Ollama is running in the background before starting the app).

**Installation**
Clone the repository:

Bash
git clone https://github.com/Oscars03/y2mp3-Music-Download.git
cd y2mp3-Music-Download
Install the required Python libraries:

Bash
pip install yt-dlp requests
Install mutagen (for ID3 tag editing):

Linux/Ubuntu users (Recommended to avoid environment conflicts):

Bash
sudo apt install python3-mutagen
Windows/Mac users:

Bash
pip install mutagen
💻 Usage
Run the V2 downloader:

Bash
python3 music_downloaderV2.py
Paste a YouTube Video URL or Playlist URL.

(Optional) Set the number of songs to download. Leave it blank to download the entire playlist.

Check/Uncheck the "Popup Confirm" box depending on whether you want to approve names manually.

Click Start. The files will be downloaded to your system's default Music folder.

⚠️ Notes
The Llama 3.1 model must be running locally on port 11434 (Ollama's default).

If yt-dlp encounters an error fetching info, ensure your yt-dlp package is up to date (pip install --upgrade yt-dlp). Private or deleted videos in playlists will be safely skipped.
