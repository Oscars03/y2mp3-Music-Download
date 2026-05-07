#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import threading
import re

# Automatically find the current user's Music folder
DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Music")

def download_music():
    url = url_entry.get().strip()
    num_songs = num_entry.get().strip()
    
    if not url:
        messagebox.showwarning("Warning", "กรุณาใส่ URL ของ YouTube")
        reset_ui()
        return

    # Check and create the download folder
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
    os.chdir(DOWNLOAD_PATH)

    # Base yt-dlp command
    command = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", "%(title)s.%(ext)s",
        "--replace-in-metadata", "title", r"(?i)\s*(\[.*?\]|\(.*?\)|【.*?】|official(.*?)(video|mv|audio)|lyrics)\s*", "",
        "--replace-in-metadata", "title", r"[\|｜]+", "",
        "--add-metadata",
        "--embed-thumbnail",
        "--newline" # Forces yt-dlp to output progress on new lines
    ]

    # Add playlist limits if a number is specified
    if num_songs.isdigit() and int(num_songs) > 0:
        command.extend(["--playlist-items", f"1-{num_songs}"])
    
    command.append(url)

    update_status("กำลังดาวน์โหลด... (Downloading...)", "blue")
    counter_label.config(text="กำลังเตรียมข้อมูล... (Preparing...)")
    
    # Reset Log and Progress Bar
    clear_log()
    progress_var.set(0)

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Read the terminal output line by line
        for line in process.stdout:
            # Process and clean the log line before showing it
            clean_line = process_log_line(line)
            if clean_line:
                write_log(clean_line)

        process.wait()

        if process.returncode == 0:
            update_status("ดาวน์โหลดสำเร็จ! (Success!)", "green")
            counter_label.config(text="เสร็จสิ้น! (Completed!)")
            progress_var.set(100) 
            amount_text = f"{num_songs} เพลง" if num_songs else "ทั้งหมด"
            messagebox.showinfo("Success", f"ดาวน์โหลดเรียบร้อยแล้วจำนวน {amount_text}\nไฟล์บันทึกอยู่ที่:\n{DOWNLOAD_PATH}")
        else:
            update_status("เกิดข้อผิดพลาด (Error)", "red")
            messagebox.showerror("Error", "เกิดข้อผิดพลาดในการดาวน์โหลด กรุณาตรวจสอบ Log")
            
    except Exception as e:
        update_status("Error: " + str(e), "red")
        write_log(f"\n❌ System Error: {str(e)}\n")
    finally:
        reset_ui()

def process_log_line(line):
    """Filters messy yt-dlp output into clean, easy-to-read English words"""
    
    # 1. Update the Progress Bar (Hide this spam from the text log)
    percent_match = re.search(r'\[download\]\s+(\d+\.\d+)%', line)
    if percent_match:
        progress_var.set(float(percent_match.group(1)))
        return None # Return None so it doesn't print to the text box
        
    # 2. Track Playlist Progress (Song X of Y)
    item_match = re.search(r'Downloading (?:video|item) (\d+) of (\d+)', line)
    if item_match:
        current, total = item_match.group(1), item_match.group(2)
        counter_label.config(text=f"Downloading: {current} / {total}")
        return f"\nStarting track {current} of {total}...\n"

    # 3. Translate technical logs to simple English words
    if "[youtube]" in line: 
        return "Finding video info...\n"
    elif "Destination:" in line and "[download]" in line: 
        return "Downloading...\n"
    elif "[ExtractAudio]" in line: 
        return "Converting to MP3...\n"
    elif "[Metadata]" in line or "[ThumbnailsConvertor]" in line or "[ModifyChapters]" in line: 
        return "Applying metadata and cover art...\n"
    elif "Deleting original file" in line: 
        return "Cleaning up temporary files...\n"
    elif "has already been downloaded" in line: 
        return "File already exists, skipping download...\n"
    elif "ERROR" in line.upper(): 
        return f"Error: {line.strip()}\n"
    
    # If the line doesn't match our clean list, ignore it to keep the log tidy
    return None

def write_log(text):
    log_box.config(state=tk.NORMAL)
    log_box.insert(tk.END, text)
    log_box.see(tk.END)
    log_box.config(state=tk.DISABLED)

def clear_log():
    log_box.config(state=tk.NORMAL)
    log_box.delete(1.0, tk.END)
    log_box.config(state=tk.DISABLED)

def start_download():
    download_btn.config(state=tk.DISABLED)
    threading.Thread(target=download_music, daemon=True).start()

def update_status(text, color):
    status_label.config(text=text, fg=color)
    root.update_idletasks()

def reset_ui():
    download_btn.config(state=tk.NORMAL)

# --- GUI Setup ---
root = tk.Tk()
root.title("Y2MP3 Downloader")
root.geometry("600x630") 
root.resizable(False, False)

# URL Input
tk.Label(root, text="วางลิงก์ YouTube (Video หรือ Playlist):", font=("Arial", 11)).pack(pady=(15, 5))
url_entry = tk.Entry(root, width=65, font=("Arial", 10))
url_entry.pack(pady=5)
url_entry.focus_set()

# Number of Songs Input
tk.Label(root, text="จำนวนเพลงที่ต้องการ (เว้นว่างไว้ถ้าจะโหลดทั้งหมด):", font=("Arial", 11)).pack(pady=(10, 5))
num_entry = tk.Entry(root, width=15, justify='center', font=("Arial", 10))
num_entry.insert(0, "10")
num_entry.pack(pady=5)

# Download Button
download_btn = tk.Button(root, text="เริ่มดาวน์โหลด (Start Download)", command=start_download, 
                         bg="#E53935", fg="white", font=("Arial", 11, "bold"), padx=20, pady=5)
download_btn.pack(pady=15)

# Song Counter Label (NEW)
counter_label = tk.Label(root, text="รอการดาวน์โหลด... (Waiting...)", font=("Arial", 10, "bold"), fg="#0078D4")
counter_label.pack(pady=0)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=500, mode='determinate')
progress_bar.pack(pady=10)

# Log Frame
log_frame = tk.Frame(root)
log_frame.pack(pady=5)

log_scrollbar = tk.Scrollbar(log_frame)
log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

log_box = tk.Text(log_frame, height=10, width=70, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 9), 
                  state=tk.DISABLED, yscrollcommand=log_scrollbar.set)
log_box.pack(side=tk.LEFT, fill=tk.BOTH)
log_scrollbar.config(command=log_box.yview)

# Status Label
status_label = tk.Label(root, text=f"พร้อมใช้งาน\n(บันทึกไฟล์ที่: {DOWNLOAD_PATH})", font=("Arial", 9), fg="#555555")
status_label.pack(pady=10)

root.mainloop()