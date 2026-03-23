# Gamdl GUI

Gamdl GUI is a modern, user-friendly graphical interface for [gamdl](https://github.com/gamdl/gamdl) (an Apple Music Downloader), built with Python and `customtkinter`. It provides an easy way to download songs, albums, playlists, and music videos from Apple Music without needing to use the command line directly.


<img width="1700" height="1356" alt="image" src="https://github.com/user-attachments/assets/da27eb86-1c9d-455b-b0d8-6bdbc14422a2" />



## Features

- **Modern Interface**: Built with `customtkinter` for a sleek, dark/light mode compatible interface.
- **Easy Cookie Management**: Easily choose and import your `cookies.txt` file directly from the app.
- **Batch Downloading**: Paste multiple Apple Music URLs (songs, albums, playlists, videos) and download them all at once.
- **Customizable Output**: Choose your download directory easily (defaults to `~/Downloads/Apple Music`).
- **Download Options**: 
  - Toggle saving cover images.
  - Disable synced lyrics.
  - Choose Download Mode (`ytdlp` or `nm3u8dlre`).
  - Set Log Level (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
- **Real-time Console**: View the download progress and logs directly within the app window.

## Prerequisites

Before using Gamdl GUI, make sure you have the following installed:

1. **Python 3.8** or higher
2. **gamdl**: The core downloader. You can install it via pip:
   ```bash
   pip install gamdl
   ```
   *Note: `gamdl` requires additional dependencies like `ffmpeg` and decryption tools. Please refer to the [gamdl documentation](https://github.com/gamdl/gamdl) for full setup instructions to ensure it works correctly.*

## Installation

1. Clone this repository or download the source code:
   ```bash
   git clone https://github.com/carlchina/Gamdl_GUI.git
   cd gamdl_gui
   ```

2. Install the required Python GUI packages:
   ```bash
   pip install customtkinter
   ```

## Usage

Run the GUI application using Python:

```bash
python gamdl_gui.py
```

### Quick Start Guide

1. **Import Cookies**: Click "Import cookies.txt" on the left sidebar and select the `cookies.txt` file from your browser (Apple Music requires cookies for downloading).
2. **Paste URLs**: Enter your Apple Music URLs in the main text box (one per line). Supported links include songs, albums, playlists, stations, and music-videos.
3. **Select Output Directory**: Choose where you want your media saved.
4. **Configure Options**: Adjust download mode, log level, and check options like "Save Cover Image" or "Disable Synced Lyrics" as needed.
5. **Start Download**: Click **"Start Download 🎉"** and watch the progress in the log console at the bottom of the window.
