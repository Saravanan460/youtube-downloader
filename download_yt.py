import yt_dlp
import subprocess
import os
import re

# === SET YOUR DEFAULT PATH HERE ===
DEFAULT_PATH = r"E:\edits\Editzzz\@ssets\music"

# --- Helper Functions ---
def time_to_sec(time_str):
    """Converts a MM:SS or HH:MM:SS string into total seconds. Returns None if empty."""
    if not time_str.strip(): 
        return None
    parts = time_str.split(':')
    parts.reverse() 
    total_seconds = 0
    for i, part in enumerate(parts):
        total_seconds += int(part) * (60 ** i)
    return total_seconds

def sanitize_filename(title):
    """Removes characters that Windows hates in filenames, and shortens long captions."""
    clean_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
    return clean_title[:80] # Keeps filenames from getting insanely long

def clear_console():
    """Clears the terminal for a clean UI."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Main Interactive Downloader ---
def interactive_downloader():
    clear_console()
    print("==============================================")
    print("🎬 UNIVERSAL DOWNLOADER & TRIMMER (YT & INSTA)")
    print("==============================================\n")

    # 1. Get URL
    url = input("🔗 Paste YouTube or Instagram URL: ").strip()
    if not url:
        print("No URL provided. Exiting...")
        return

    # 2. Get Format
    print("\n📦 Choose Format:")
    print("  [1] Video (MP4)")
    print("  [2] Audio Only (MP3)")
    format_choice = input("👉 Enter 1 or 2 [Default 1]: ").strip()
    is_audio = (format_choice == '2')

    # 3. Get Video Quality
    quality_str = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' # Default 1080p
    if not is_audio:
        print("\n⚙️ Choose Video Quality:")
        print("  [1] 1080p (Standard High Quality)")
        print("  [2] 720p (Smaller File Size)")
        print("  [3] Maximum Quality (4K/Highest Available)")
        vid_choice = input("👉 Enter 1, 2, or 3 [Default 1]: ").strip()
        
        if vid_choice == '2':
            quality_str = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif vid_choice == '3':
            quality_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    # 4. Get Trim Times
    print("\n✂️ Trimming Options (Press ENTER to skip and download full video):")
    start_input = input("  Start Time (e.g., 3:23): ").strip()
    end_input = input("  End Time   (e.g., 4:01): ").strip()
    
    start_sec = time_to_sec(start_input)
    end_sec = time_to_sec(end_input)

    # 5. Get Download Path
    print(f"\n📂 Choose Save Location:")
    print(f"  [1] Default: {DEFAULT_PATH}")
    print(f"  [2] Enter a new path manually")
    path_choice = input("👉 Enter 1 or 2 [Default 1]: ").strip()

    if path_choice == '2':
        download_path = input("  ✏️ Paste new folder path: ").strip()
        if not download_path:
            download_path = DEFAULT_PATH
    else:
        download_path = DEFAULT_PATH

    # Ensure the folder exists
    if not os.path.exists(download_path):
        try:
            os.makedirs(download_path)
            print(f"  [+] Created new folder: {download_path}")
        except Exception as e:
            print(f"  [!] Could not create folder. Saving to current directory instead.")
            download_path = "."

    # --- Fetching Title First ---
    print("\n⏳ Fetching official title...")
    
    # Setup temporary configuration just to grab metadata safely
    meta_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(meta_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            raw_title = info.get('title', 'Downloaded_Media')
            if not raw_title: 
                raw_title = "Instagram_Reel"
            safe_title = sanitize_filename(raw_title)
        except Exception as e:
            print(f"\n❌ Error fetching video info: {e}")
            return

    # --- Setup Output Names & Paths ---
    final_ext = "mp3" if is_audio else "mp4"
    final_filepath = os.path.join(download_path, f"{safe_title}.{final_ext}")
    
    # Remove old final file if it exists to prevent overwrite crashes
    if os.path.exists(final_filepath):
        os.remove(final_filepath)

    # Setup core yt-dlp dictionary
    ydl_opts = {
        'http_chunk_size': 10485760,
        'quiet': False, 
        'no_warnings': True
    }

    # Handle Trimming vs Full Download Naming Logic
    is_trimming = (start_sec is not None and end_sec is not None)
    
    if is_trimming:
        # Use a generic placeholder layout that yt-dlp will substitute with .mp3 or .mp4
        ydl_opts['outtmpl'] = os.path.join(download_path, 'temp_clip_process.%(ext)s')
        actual_temp_file = os.path.join(download_path, f'temp_clip_process.{final_ext}')
        if os.path.exists(actual_temp_file):
            os.remove(actual_temp_file)
    else:
        # Direct Download Mode: writes straight to the correct title layout completely bypassing temp
        ydl_opts['outtmpl'] = os.path.join(download_path, f'{safe_title}.%(ext)s')

    # Apply specific audio/video quality rules
    if is_audio:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['format'] = quality_str

    # --- Run Download ---
    print(f"📥 Downloading: '{safe_title}'...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl_actual:
        try:
            ydl_actual.download([url])
        except Exception as e:
            print(f"\n❌ Error during download processing: {e}")
            return

    # --- Local Trimming Only If Requested ---
    if is_trimming:
        print(f"\n🔪 Slicing locally from {start_input} to {end_input}...")
        cmd = [
            'ffmpeg', '-y', '-i', actual_temp_file, 
            '-ss', str(start_sec), '-to', str(end_sec), 
            '-c', 'copy', final_filepath
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Clean up the temporary video/audio file completely
        if os.path.exists(actual_temp_file):
            os.remove(actual_temp_file)
            print("🧹 Cleaned up temporary stream files.")
            
        print(f"\n✅ DONE! Sliced clip saved as: \n📂 {os.path.abspath(final_filepath)}")
        
    else:
        print(f"\n✅ DONE! Full file saved directly as: \n📂 {os.path.abspath(final_filepath)}")

if __name__ == "__main__":
    interactive_downloader()