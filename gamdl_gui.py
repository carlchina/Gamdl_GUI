import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import sys
import os
import shutil

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class GamdlGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Gamdl GUI - Apple Music Downloader")
        self.geometry("850x650")
        
        # main layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Gamdl GUI", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Cookie selection
        self.cookie_label = ctk.CTkLabel(self.sidebar_frame, text="Cookies File (cookies.txt):")
        self.cookie_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.cookie_btn = ctk.CTkButton(self.sidebar_frame, text="Import cookies.txt")
        self.cookie_btn.grid(row=2, column=0, padx=20, pady=5)
        self.cookie_btn.bind("<Button-1>", self.select_cookie)
        self.cookie_path = ""
        
        # Log level
        self.log_level_label = ctk.CTkLabel(self.sidebar_frame, text="Log Level:")
        self.log_level_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.log_level_var = ctk.StringVar(value="INFO")
        self.log_level_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["DEBUG", "INFO", "WARNING", "ERROR"], variable=self.log_level_var)
        self.log_level_menu.grid(row=4, column=0, padx=20, pady=5)
        
        # Download Mode
        self.dl_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Download Mode:")
        self.dl_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.dl_mode_var = ctk.StringVar(value="ytdlp")
        self.dl_mode_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["ytdlp", "nm3u8dlre"], variable=self.dl_mode_var)
        self.dl_mode_menu.grid(row=6, column=0, padx=20, pady=5)
        
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="Version: 0.5 By Carlchina", text_color="gray", font=ctk.CTkFont(size=10))
        self.version_label.grid(row=8, column=0, padx=20, pady=(0, 0), sticky="s")
        
        # Action button
        self.download_btn = ctk.CTkButton(self.sidebar_frame, text="Start Download 🎉", height=40)
        self.download_btn.grid(row=9, column=0, padx=20, pady=(10, 20), sticky="s")
        self.download_btn.bind("<Button-1>", self.start_download)
        
        # Main content
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(8, weight=1)
        
        # URL
        self.url_label = ctk.CTkLabel(self.main_frame, text="🎵 Apple Music URLs (songs, albums, videos, one per line):", font=ctk.CTkFont(weight="bold"))
        self.url_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        self.url_textbox = ctk.CTkTextbox(self.main_frame, height=100)
        self.url_textbox.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        # Output directory
        self.out_dir_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.out_dir_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.out_dir_frame.grid_columnconfigure(1, weight=1)
        
        self.out_dir_label = ctk.CTkLabel(self.out_dir_frame, text="Output Directory:")
        self.out_dir_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.out_dir_entry = ctk.CTkEntry(self.out_dir_frame, width=300)
        # Default downloads folder
        default_dl = os.path.join(os.path.expanduser("~"), "Downloads", "Apple Music")
        self.out_dir_entry.insert(0, default_dl)
        self.out_dir_entry.grid(row=0, column=1, sticky="ew")
        self.out_dir_btn = ctk.CTkButton(self.out_dir_frame, text="Browse", width=80)
        self.out_dir_btn.grid(row=0, column=2, padx=(10, 0))
        self.out_dir_btn.bind("<Button-1>", self.select_out_dir)
        
        # Settings frame
        self.settings_frame = ctk.CTkFrame(self.main_frame)
        self.settings_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.settings_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Options frame
        self.opts_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.opts_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 10))

        # Save Cover checkbox
        self.save_cover_var = ctk.BooleanVar(value=True)
        self.save_cover_cb = ctk.CTkCheckBox(self.opts_frame, text="Save Cover Image", variable=self.save_cover_var)
        self.save_cover_cb.grid(row=0, column=0, pady=5, sticky="w")
        
        # Synced lyrics checkbox
        self.synced_lyrics_var = ctk.BooleanVar(value=False)
        self.synced_lyrics_cb = ctk.CTkCheckBox(self.opts_frame, text="Disable Synced Lyrics", variable=self.synced_lyrics_var)
        self.synced_lyrics_cb.grid(row=0, column=1, padx=20, pady=5, sticky="w")

        # Console Output
        self.console_header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.console_header_frame.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.console_header_frame.grid_columnconfigure(0, weight=1)
        
        self.console_label = ctk.CTkLabel(self.console_header_frame, text="Log:", font=ctk.CTkFont(weight="bold"))
        self.console_label.grid(row=0, column=0, sticky="w")
        
        self.clear_console_btn = ctk.CTkButton(self.console_header_frame, text="Clear Console", width=80)
        self.clear_console_btn.grid(row=0, column=1, sticky="e")
        self.clear_console_btn.bind("<Button-1>", self.clear_console)
        self.console_textbox = ctk.CTkTextbox(self.main_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.console_textbox.grid(row=8, column=0, padx=20, pady=10, sticky="nsew")
        self.console_textbox.configure(state="disabled")

    def select_cookie(self, event=None):
        file_path = filedialog.askopenfilename(title="Select cookies.txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                gamdl_dir = os.path.join(os.path.expanduser("~"), ".gamdl")
                os.makedirs(gamdl_dir, exist_ok=True)
                dest_path = os.path.join(gamdl_dir, "cookies.txt")
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.copy(file_path, dest_path)
                self.cookie_path = dest_path
                self.cookie_btn.configure(text="cookie.txt Saved")
                self.log_console(f"[*] Cookie saved to: {dest_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy cookie file:\n{e}")

    def clear_console(self, event=None):
        self.console_textbox.configure(state="normal")
        self.console_textbox.delete("1.0", ctk.END)
        self.console_textbox.configure(state="disabled")

    def select_out_dir(self, event=None):
        dir_path = filedialog.askdirectory(title="Select Download Directory")
        if dir_path:
            self.out_dir_entry.delete(0, ctk.END)
            self.out_dir_entry.insert(0, dir_path)

    def log_console(self, text):
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert(ctk.END, text + "\n")
        self.console_textbox.see(ctk.END)
        self.console_textbox.configure(state="disabled")

    def start_download(self, event=None):
        if self.download_btn.cget("state") == "disabled":
            return
            
        urls = self.url_textbox.get("1.0", ctk.END).strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            messagebox.showerror("Error", "Please paste at least one Apple Music URL.")
            return

        cmd = ["gamdl"]
        
        if self.cookie_path:
            cmd.extend(["-c", self.cookie_path])
            
        out_dir = self.out_dir_entry.get()
        if out_dir:
            cmd.extend(["-o", out_dir])
            
        has_song = False
        has_video = False
        
        for url in urls:
            if '/music-video/' in url or '/post/' in url:
                has_video = True
            elif '/song/' in url or '/album/' in url or '/playlist/' in url or '/station/' in url:
                has_song = True
                
        # If neither is matched clearly, apply both just in case
        if not has_song and not has_video:
            has_song = True
            has_video = True

        cmd.extend(["--log-level", self.log_level_var.get()])
        cmd.extend(["--download-mode", self.dl_mode_var.get()])
        
        if has_song:
            if self.save_cover_var.get():
                cmd.append("--save-cover")
            if self.synced_lyrics_var.get():
                cmd.append("--no-synced-lyrics")
            
        cmd.extend(urls)
        
        self.log_console(f"\n[>] Executing: {' '.join(cmd)}")
        self.download_btn.configure(state="disabled")
        
        threading.Thread(target=self.run_process, args=(cmd,), daemon=True).start()

    def run_process(self, cmd):
        try:
            # Run command unbuffered
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True) # pyright: ignore
            
            for line in iter(process.stdout.readline, ''): # pyright: ignore
                self.after(0, self.log_console, line.strip())
                
            process.stdout.close() # pyright: ignore
            return_code = process.wait()
            
            if return_code == 0:
                self.after(0, self.log_console, "\n[✔] Download sequence completed successfully.")
            else:
                self.after(0, self.log_console, f"\n[!] gamdl process exited with code {return_code}")
                
        except FileNotFoundError:
            self.after(0, self.log_console, "\n[X] Error: 'gamdl' command not found. Please make sure it is installed (pip install gamdl) and in your system PATH.")
        except Exception as e:
            self.after(0, self.log_console, f"\n[X] Error launching command: {str(e)}")
            
        finally:
            self.after(0, lambda: self.download_btn.configure(state="normal"))

if __name__ == "__main__":
    app = GamdlGUI()
    app.mainloop()
