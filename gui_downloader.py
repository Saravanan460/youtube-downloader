import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import yt_dlp
import subprocess
import os
import re

# === SETTINGS ===
DEFAULT_PATH = r"E:\edits\Editzzz\@ssets\music"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def time_to_sec(time_str):
    if not time_str.strip(): return None
    parts = time_str.split(':')
    parts.reverse() 
    return sum(int(part) * (60 ** i) for i, part in enumerate(parts))

def sanitize_filename(title):
    clean_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
    return clean_title[:80]

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Downloader Pro")
        self.root.geometry("650x520") # Slightly taller to fit the buttons beautifully
        self.root.resizable(False, False)
        
        self.is_cancelled = False # The Kill Switch Flag
        
        self.frame = ctk.CTkFrame(root, corner_radius=15)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.title_label = ctk.CTkLabel(self.frame, text="🎬 Universal Media Downloader", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(20, 20))

        # 1. URL
        ctk.CTkLabel(self.frame, text="🔗 Media URL:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=20, pady=10, sticky='w')
        self.url_entry = ctk.CTkEntry(self.frame, width=380, placeholder_text="Paste YouTube or Instagram link here...")
        self.url_entry.grid(row=1, column=1, columnspan=2, pady=10, sticky='w')

        # 2. Format
        ctk.CTkLabel(self.frame, text="📦 Format:", font=ctk.CTkFont(size=14)).grid(row=2, column=0, padx=20, pady=10, sticky='w')
        self.format_combo = ctk.CTkComboBox(self.frame, values=["Video (MP4)", "Audio Only (MP3)"], width=380, state="readonly", command=self.update_quality_options)
        self.format_combo.set("Video (MP4)")
        self.format_combo.grid(row=2, column=1, columnspan=2, pady=10, sticky='w')

        # 3. Quality
        ctk.CTkLabel(self.frame, text="⚙️ Quality:", font=ctk.CTkFont(size=14)).grid(row=3, column=0, padx=20, pady=10, sticky='w')
        self.quality_combo = ctk.CTkComboBox(self.frame, values=["1080p (Standard High Quality)", "720p (Smaller File Size)", "Max Quality (4K)"], width=380, state="readonly")
        self.quality_combo.set("1080p (Standard High Quality)")
        self.quality_combo.grid(row=3, column=1, columnspan=2, pady=10, sticky='w')

        # 4. Trimming
        ctk.CTkLabel(self.frame, text="✂️ Trim (Optional):", font=ctk.CTkFont(size=14)).grid(row=4, column=0, padx=20, pady=10, sticky='w')
        trim_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        trim_frame.grid(row=4, column=1, columnspan=2, sticky='w')
        
        ctk.CTkLabel(trim_frame, text="Start:").pack(side="left", padx=(0, 5))
        self.start_entry = ctk.CTkEntry(trim_frame, width=80, placeholder_text="0:00")
        self.start_entry.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(trim_frame, text="End:").pack(side="left", padx=(0, 5))
        self.end_entry = ctk.CTkEntry(trim_frame, width=80, placeholder_text="3:23")
        self.end_entry.pack(side="left")

        # 5. Save Location
        ctk.CTkLabel(self.frame, text="📂 Save To:", font=ctk.CTkFont(size=14)).grid(row=5, column=0, padx=20, pady=10, sticky='w')
        self.path_entry = ctk.CTkEntry(self.frame, width=280)
        self.path_entry.insert(0, DEFAULT_PATH)
        self.path_entry.grid(row=5, column=1, pady=10, sticky='w')
        
        self.browse_btn = ctk.CTkButton(self.frame, text="Browse", width=80, command=self.browse_folder, fg_color="gray30", hover_color="gray20")
        self.browse_btn.grid(row=5, column=2, pady=10, padx=(10, 0), sticky='w')

        # --- Button Frame (Download & Cancel) ---
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=3, pady=(20, 10), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        self.download_btn = ctk.CTkButton(btn_frame, text="DOWNLOAD NOW", font=ctk.CTkFont(size=15, weight="bold"), height=45, command=self.start_download)
        self.download_btn.grid(row=0, column=0, padx=(20, 10), sticky="ew")

        self.cancel_btn = ctk.CTkButton(btn_frame, text="CANCEL", font=ctk.CTkFont(size=15, weight="bold"), height=45, fg_color="#e74c3c", hover_color="#c0392b", state="disabled", command=self.cancel_download)
        self.cancel_btn.grid(row=0, column=1, padx=(10, 20), sticky="ew")

        self.status_var = ctk.StringVar(value="Status: Ready")
        self.status_label = ctk.CTkLabel(self.frame, textvariable=self.status_var, text_color="gray60")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)

    def update_quality_options(self, choice):
        if choice == "Audio Only (MP3)":
            self.quality_combo.configure(values=["320kbps (Studio Quality)", "192kbps (Standard Quality)", "128kbps (Basic Size)"])
            self.quality_combo.set("320kbps (Studio Quality)")
        else:
            self.quality_combo.configure(values=["1080p (Standard High Quality)", "720p (Smaller File Size)", "Max Quality (4K)"])
            self.quality_combo.set("1080p (Standard High Quality)")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.path_entry.get())
        if folder:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, folder)

    def set_status(self, text, color="white"):
        self.status_var.set(text)
        self.status_label.configure(text_color=color)
        self.root.update_idletasks()

    # --- Live Progress Hook & Kill Switch ---
    def my_hook(self, d):
        # The exact moment the user clicks cancel, this triggers an error to kill the download
        if self.is_cancelled:
            raise ValueError("CANCELLED_BY_USER")

        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', '0KiB/s').strip()
            percent = re.sub(r'\x1b\[[0-9;]*m', '', percent)
            speed = re.sub(r'\x1b\[[0-9;]*m', '', speed)
            
            self.root.after(0, lambda: self.set_status(f"📥 Downloading: {percent} (Speed: {speed})", "#3498db"))

    def cancel_download(self):
        self.is_cancelled = True
        self.set_status("🛑 Stopping download and cleaning up...", "#e74c3c")
        self.cancel_btn.configure(state="disabled")

    def start_download(self):
        self.is_cancelled = False
        self.download_btn.configure(state="disabled", text="PROCESSING...")
        self.cancel_btn.configure(state="normal")
        
        params = {
            'url': self.url_entry.get().strip(),
            'is_audio': self.format_combo.get() == "Audio Only (MP3)",
            'quality_idx': self.quality_combo.get(),
            'start_in': self.start_entry.get().strip(),
            'end_in': self.end_entry.get().strip(),
            'path': self.path_entry.get().strip() or "."
        }
        
        if not params['url']:
            messagebox.showwarning("Missing URL", "Please paste a media link first!")
            self.download_btn.configure(state="normal", text="DOWNLOAD NOW")
            self.cancel_btn.configure(state="disabled")
            return

        threading.Thread(target=self.process_download, args=(params,), daemon=True).start()

    def process_download(self, p):
        actual_temp_file = ""
        final_filepath = ""
        
        try:
            self.set_status("⏳ Fetching video information...", "#3498db")
            if self.is_cancelled: raise ValueError("CANCELLED_BY_USER")

            start_sec = time_to_sec(p['start_in'])
            end_sec = time_to_sec(p['end_in'])

            meta_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(meta_opts) as ydl:
                info = ydl.extract_info(p['url'], download=False)
                raw_title = info.get('title', 'Downloaded_Media') or "Instagram_Reel"
                safe_title = sanitize_filename(raw_title)

            final_ext = "mp3" if p['is_audio'] else "mp4"
            final_filepath = os.path.join(p['path'], f"{safe_title}.{final_ext}")
            
            if os.path.exists(final_filepath):
                os.remove(final_filepath)

            ydl_opts = {
                'http_chunk_size': 10485760, 
                'quiet': True, 
                'no_warnings': True,
                'progress_hooks': [self.my_hook] 
            }
            
            is_trimming = (start_sec is not None and end_sec is not None)
            
            if is_trimming:
                actual_temp_file = os.path.join(p['path'], f'temp_clip_process.{final_ext}')
                ydl_opts['outtmpl'] = os.path.join(p['path'], 'temp_clip_process.%(ext)s')
                if os.path.exists(actual_temp_file): os.remove(actual_temp_file)
            else:
                ydl_opts['outtmpl'] = os.path.join(p['path'], f'{safe_title}.%(ext)s')
                actual_temp_file = final_filepath # Map temp to final for cleanup if cancelled

            if p['is_audio']:
                audio_kbps = p['quality_idx'].split('k')[0]
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': audio_kbps}]
            else:
                if "720p" in p['quality_idx']:
                    ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                elif "4K" in p['quality_idx']:
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

            self.set_status(f"📥 Downloading: {safe_title}...", "#f1c40f")
            
            # This is where the kill switch triggers if cancelled
            with yt_dlp.YoutubeDL(ydl_opts) as ydl_actual:
                ydl_actual.download([p['url']])

            if is_trimming:
                self.set_status("🔪 Slicing media perfectly...", "#e67e22")
                cmd = ['ffmpeg', '-y', '-i', actual_temp_file, '-ss', str(start_sec), '-to', str(end_sec), '-c', 'copy', final_filepath]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(actual_temp_file): os.remove(actual_temp_file)
            
            self.set_status("✅ Download Complete!", "#2ecc71")
            messagebox.showinfo("Success", f"File saved successfully!\n\nLocation: {final_filepath}")

        except Exception as e:
            if "CANCELLED_BY_USER" in str(e):
                self.set_status("🚫 Download Cancelled.", "#e74c3c")
            else:
                self.set_status("❌ Error occurred.", "#e74c3c")
                messagebox.showerror("Error", str(e))
                
            # --- THE CLEANUP CREW ---
            # Automatically hunts down and deletes half-downloaded .part files
            files_to_delete = [
                actual_temp_file, 
                actual_temp_file + ".part", 
                actual_temp_file + ".ytdl",
                final_filepath,
                final_filepath + ".part",
                final_filepath + ".ytdl"
            ]
            for f in files_to_delete:
                if f and os.path.exists(f):
                    try: os.remove(f)
                    except: pass

        finally:
            self.download_btn.configure(state="normal", text="DOWNLOAD NOW")
            self.cancel_btn.configure(state="disabled")

if __name__ == "__main__":
    root = ctk.CTk()
    app = DownloaderApp(root)
    root.mainloop()