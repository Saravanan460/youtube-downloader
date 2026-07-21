Here is the clean, formatted, and copy-paste-ready `README.md` for your GitHub repository. It focuses entirely on getting users set up quickly, explains the necessary FFmpeg/Node.js steps simply, and shows them how to make the invisible desktop shortcut!

---

# 🎬 Universal Media Downloader Pro

A lightweight, modern Windows desktop application for downloading and instantly trimming high-quality media from YouTube and Instagram. Built with Python, yt-dlp, FFmpeg, and CustomTkinter.

Universal Media Downloader Pro is a sleek, Python-based desktop application designed to solve the frustrations of slow, ad-filled web downloaders. It uses multi-threaded connections to bypass network throttling and allows for instant, precision video trimming without the need for slow frame-by-frame re-encoding.

---

## ✨ Features

* 🖥️ **Premium Desktop UI:** A dark-themed, native Windows experience built with CustomTkinter—no ugly terminal windows.


* 🚀 **Max Download Speeds:** Implemented a multi-threaded architecture that opens up 10 simultaneous connections to blast past standard network speed limits.


* ✂️ **Instant Precision Trimming:** Input exact timestamps, and the app uses FFmpeg to instantly slice the video exactly where you need it.


* 🎬 **Strict Quality Locks:** The UI is dynamic—if you select video, it lets you force 1080p or 4K resolution. If you select audio, it automatically swaps the menu so you can extract pristine 320kbps audio.


* 📊 **Live Progress Tracker:** The UI features a real-time tracker displaying the exact download percentage and network speed (e.g., 3.52 MiB/s) while it works.


* 🛑 **The "Kill Switch":** I added a bright red "Cancel" button that injects a "poison pill" to instantly abort the download and triggers a cleanup crew to delete any leftover junk (.part) files from your hard drive.


* 📁 **Smart Save & Browse:** A built-in Browse button lets you pick your exact destination path, and the app automatically fetches the official video title to name your file perfectly.



---

## 🛠️ Installation & Setup

Getting this running on your local Windows machine takes just a few minutes.

### Step 1: Clone the Repository

Download this repository to your computer and navigate to the project folder.

### Step 2: Install Python Dependencies

Open your terminal (or activate your virtual environment/Conda environment) and install the required Python libraries:

```bash
pip install yt-dlp customtkinter

```

(Note: yt-dlp and CustomTkinter are the only Python packages required).

### Step 3: Install Node.js (For 1080p Bypass)

YouTube sends complex JavaScript "puzzles" to verify the user wasn't a bot. If you don't have a JavaScript engine installed, YouTube will block high-quality video downloads.

1. Go to [nodejs.org](https://nodejs.org/) and download the Windows installer (LTS version).


2. Install it using the default settings.
3. yt-dlp automatically detected the JS engine and used it to quietly solve the puzzles in the background, unlocking maximum download speeds and restoring 1080p access.



### Step 4: Add FFmpeg (The Portable Way)

To trim videos instantly, you need FFmpeg. Instead of messing with messy system PATH variables, we use a portable method:

1. Download the raw `ffmpeg.exe` and `ffprobe.exe` binaries directly from Gyan.dev. (Grab the "ffmpeg-release-essentials.zip" build) .


2. Open the `.zip`, go into the `bin` folder, and copy `ffmpeg.exe` and `ffprobe.exe`.


3. Drop them directly into the Python project folder right next to the `gui_downloader.py` script.



---

## 🪄 Usage: The "Magic" Desktop Shortcut

You *can* run this app from the terminal using `python gui_downloader.py`, but normal Python runs on python.exe, which forces that black terminal to open. Here is how to run it like a real desktop app:

1. Right-click on your Windows Desktop and select **New > Shortcut**.
2. Instead, we route the shortcut to pythonw.exe (the "w" stands for windowed). This tells your computer to run the Python engine completely invisibly in the background.


3. In the location box, you need to combine your Python Environment Path and your Script Path:


`[Your Environment Path\pythonw.exe] "[Your Script Path\gui_downloader.py]"`.


**Example:**
```text
C:\Users\Username\miniconda3\envs\ytdlp_env\pythonw.exe "E:\Projects\youtube_downloader\gui_downloader.py"

```


⚠️ **Crucial Detail:** You must wrap your script path in quotes! If your project folder has a space in its name (like youtube downloader), Windows will stop reading at the space, fail to find the file, and instantly crash.


4. Click **Next**, name the shortcut "Media Downloader", and hit **Finish**.

I just double-click a custom icon on my desktop, and my sleek UI pops up instantly while the backend code remains completely hidden. Paste your link, choose your quality, set your trim times, and hit Download!
