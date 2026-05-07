#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import threading
import re
import requests
import json
import sys

# 🟢 ตรวจสอบว่าติดตั้ง mutagen หรือยัง
try:
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3NoHeaderError, ID3
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", "กรุณาติดตั้งไลบรารีก่อนรันโปรแกรม:\nsudo apt install python3-mutagen\nหรือ\npip install mutagen")
    sys.exit(1)

# --- Configuration ---
DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Music")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

class NameConfirmDialog:
    def __init__(self, parent, original_name, ai_name):
        self.result = ai_name
        self.is_cancelled = False  
        self.event = threading.Event()
        
        parent.after(0, self.show_dialog, parent, original_name, ai_name)
        self.event.wait()

    def show_dialog(self, parent, original_name, ai_name):
        self.top = tk.Toplevel(parent)
        self.top.title("ตรวจสอบและแก้ไขชื่อเพลง")
        self.top.geometry("550x280") 
        self.top.resizable(False, False)
        self.top.attributes('-topmost', True)
        self.top.grab_set() 

        tk.Label(self.top, text="ชื่อต้นฉบับจาก YouTube (คลุมดำเพื่อ Copy ได้):", font=("Arial", 10)).pack(pady=(15, 5))
        
        self.orig_entry = tk.Entry(self.top, width=65, font=("Arial", 10), fg="#555555", justify='center')
        self.orig_entry.insert(0, original_name)
        self.orig_entry.config(state='readonly')
        self.orig_entry.pack(pady=(0, 10))

        tk.Label(self.top, text="ชื่อที่ Llama 3.1 เสนอ (แก้ไขได้ในช่องนี้):", font=("Arial", 10, "bold"), fg="#1565C0").pack(pady=5)
        
        self.entry = tk.Entry(self.top, width=65, font=("Arial", 12), justify='center')
        self.entry.insert(0, ai_name)
        self.entry.pack(pady=5)
        self.entry.focus_set()

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="✅ ยืนยัน (Confirm)", command=self.on_confirm, 
                  bg="#2E7D32", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ ข้ามเพลงนี้ (Skip)", command=self.on_cancel, 
                  bg="#D32F2F", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5).pack(side=tk.LEFT, padx=10)

        self.top.protocol("WM_DELETE_WINDOW", self.on_close)
        self.top.bind('<Return>', lambda e: self.on_confirm())

    def on_confirm(self):
        self.result = self.entry.get().strip()
        self.top.grab_release()
        self.top.destroy()
        self.event.set()

    def on_cancel(self):
        self.is_cancelled = True 
        self.top.grab_release()
        self.top.destroy()
        self.event.set()

    def on_close(self):
        self.is_cancelled = True 
        self.top.grab_release()
        self.top.destroy()
        self.event.set()

def clean_title_with_llama(raw_title, channel_name):
    import re
    
    # 🟢 0. ตรวจจับคำว่า Live จากชื่อต้นฉบับก่อน (เพราะเดี๋ยววงเล็บอาจถูกลบทิ้ง)
    # (?i) คือไม่สนตัวพิมพ์เล็ก/ใหญ่, \blive\b คือหาคำว่า live เป็นคำๆ 
    is_live = bool(re.search(r'(?i)\blive\b', raw_title))

    # 🟢 1. Python Pre-cleaning (ทำความสะอาดชื่อคลิปก่อน)
    safe_title = re.sub(r'(?i)(\[.*?\]|\(.*?\)|\|.*?\||Official.*?MV|Audio|Lyrics|HD|4K)', '', raw_title)
    safe_title = re.sub(r'[\|｜]+', '', safe_title).strip()
    safe_title = safe_title.strip('- ') 
    
    # 🟢 2. ตรวจสอบว่ามีชื่อศิลปินในคลิปไหม ถ้าไม่มี ให้ดึงชื่อช่องมาใช้
    if "-" not in safe_title and channel_name and channel_name != "NA":
        clean_channel = re.sub(r'(?i)(official|channel|vevo|music|thailand)', '', channel_name).strip()
        clean_channel = re.sub(r'([a-z])([A-Z])', r'\1 \2', clean_channel).strip()
        safe_title = f"{safe_title} - {clean_channel}"

    # 🟢 3. ฟังก์ชันตัวช่วยสำหรับแทรก [Live] หลังชื่อเพลง
    def insert_live_tag(title_str):
        if not is_live: return title_str
        parts = title_str.split(" - ")
        if len(parts) >= 2:
            # เอา [Live] ไปต่อท้ายส่วนที่เป็นชื่อเพลง (ก่อนเครื่องหมาย - ตัวสุดท้าย)
            parts[-2] = parts[-2].strip() + " [Live]"
            return " - ".join(parts)
        else:
            return title_str.strip() + " [Live]"

    # 🟢 4. ส่งให้ AI สลับตำแหน่ง
    prompt = (
        "Format the following music title strictly as 'Song Name - Artist Name'.\n"
        "CRITICAL RULES:\n"
        "1. DO NOT translate, invent, or change words. Copy the exact text.\n"
        "2. 'Only Monday', 'Three Man Down', 'Tilly Birds', 'COCKTAIL', 'TaitosmitH', 'TATTOO COLOUR', 'LITTLE JOHN', 'กู่แคน', 'มนัสวีร์', 'LHAM SOMPHOL', 'แหลม สมพล' are BAND NAMES (Artists).\n"
        "3. EXCEPTION: If you see the artist 'manutsawee' (in English), you MUST change it to 'มนัสวีร์'.\n"
        "4. Return ONLY the formatted string. No chat, no explanations.\n\n"
        "Example 1:\n"
        "Input: ทิ้งไป - Only Monday\n"
        "Output: ทิ้งไป - Only Monday\n\n"
        "Example 2:\n"
        "Input: manutsawee - โลกที่แบกไว้\n"
        "Output: โลกที่แบกไว้ - มนัสวีร์\n\n"
        f"Input: {safe_title}\n"
        "Output:"
    )

    try:
        response = requests.post(
            OLLAMA_URL, 
            json={
                "model": MODEL_NAME, 
                "prompt": prompt, 
                "stream": False,
                "options": {
                    "temperature": 0.0, 
                    "num_predict": 50   
                }
            }, 
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            cleaned = result.get("response", "").strip()
            
            cleaned = cleaned.replace("Output:", "").replace("output:", "").replace('"', '').strip()
            
            if cleaned and "-" in cleaned:
                final_clean = "".join(c for c in cleaned if c not in r'<>:"/\|?*').strip()
                return insert_live_tag(final_clean) # 🟢 แทรก [Live] เข้าไป
                
    except Exception as e:
        print(f"Llama Error: {e}")
        
    fallback_clean = "".join(c for c in safe_title if c not in r'<>:"/\|?*').strip()
    return insert_live_tag(fallback_clean) # 🟢 กรณี AI พัง ก็ยังแทรก [Live] ให้

# 🟢 3. ฟังก์ชันอัปเดต Metadata (รองรับ Album และ Channel Artist)
def apply_metadata_to_file(filepath, final_title, playlist_name, channel_name):
    parts = final_title.split(" - ")
    if len(parts) >= 2:
        # ถ้า AI แยก "เพลง - ศิลปิน" ได้สำเร็จ ให้ยึดตาม AI
        artist = parts[-1].strip()
        title = " - ".join(parts[:-1]).strip()
    else:
        # ถ้า AI แยกไม่ได้ ให้เอาชื่อคลิปไปใส่ช่องเพลง และเอา "ชื่อช่อง YouTube" ไปใส่ช่องศิลปินแทน
        title = final_title.strip()
        artist = channel_name if channel_name and channel_name != "NA" else ""

    try:
        try:
            audio = EasyID3(filepath)
        except ID3NoHeaderError:
            meta = ID3()
            meta.save(filepath)
            audio = EasyID3(filepath)

        audio['title'] = title
        if artist:
            audio['artist'] = artist
            
        # 🟢 ยัดชื่อ Playlist ลงในช่อง Album
        if playlist_name and playlist_name != "NA":
            audio['album'] = playlist_name
        else:
            if 'album' in audio: audio['album'] = ''

        if 'comment' in audio: audio['comment'] = ''
            
        audio.save()
        return True
    except Exception as e:
        write_log(f"⚠️ ไม่สามารถเขียน Metadata ได้: {e}\n")
        return False

def download_music():
    url = url_entry.get().strip()
    num_songs = num_entry.get().strip()
    use_popup = popup_var.get()
    
    if not url:
        messagebox.showwarning("Warning", "กรุณาใส่ URL ของ YouTube")
        reset_ui()
        return

    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
    os.chdir(DOWNLOAD_PATH)

    update_status("กำลังตรวจสอบวิดีโอ... (Fetching Info)", "purple")
    counter_label.config(text="กำลังดึงรายชื่อเพลงและข้อมูลเพลย์ลิสต์...")
    clear_log()
    progress_var.set(0)

    # 🟢 1. สั่ง yt-dlp ให้ดึง Playlist Title และ Uploader (Channel Name) มาด้วย
    write_log("Fetching video info, album, and channel details...\n")
    info_cmd = [
        "yt-dlp", "--ignore-errors", "--flat-playlist", 
        "--print", "%(title)s___SPLIT___%(id)s___SPLIT___%(playlist_title)s___SPLIT___%(uploader)s", 
        "--no-warnings"
    ]
    if num_songs.isdigit() and int(num_songs) > 0:
        info_cmd.extend(["--playlist-items", f"1-{num_songs}"])
    info_cmd.append(url)

    try:
        result = subprocess.run(info_cmd, capture_output=True, text=True)
        info_output = result.stdout
        error_output = result.stderr
        
        video_list = []
        for line in info_output.strip().split('\n'):
            if '___SPLIT___' in line:
                parts = line.split('___SPLIT___')
                # เช็คว่าดึงข้อมูลมาครบ 4 ส่วนหรือไม่
                if len(parts) >= 4:
                    title = parts[0].strip()
                    vid = parts[1].strip()
                    playlist_name = parts[2].strip()
                    channel_name = parts[3].strip()

                    if "[Deleted video]" not in title and "[Private video]" not in title:
                        video_list.append((title, vid, playlist_name, channel_name))
        
        if not video_list and result.returncode != 0:
            raise Exception(f"\n{error_output.strip()}")
            
        if result.returncode != 0 and video_list:
            write_log("⚠️ Note: ข้ามบางวิดีโอที่ไม่สามารถเข้าถึงได้ (Private/Deleted)\n")
                
        if not video_list:
            raise Exception("ไม่พบวิดีโอ หรือลิงก์ไม่ถูกต้อง")
            
    except Exception as e:
        update_status("เกิดข้อผิดพลาดในการดึงข้อมูล", "red")
        write_log(f"❌ Error: {e}\n")
        reset_ui()
        return

    total_videos = len(video_list)
    write_log(f"Found {total_videos} videos. Starting AI pipeline...\n")

    # 🟢 แตกตัวแปรออกมาใช้งานใน Loop
    for index, (raw_title, vid, playlist_name, channel_name) in enumerate(video_list, 1):
        counter_label.config(text=f"กำลังประมวลผล: {index} / {total_videos}")
        
        update_status(f"Llama 3.1 กำลังวิเคราะห์... ({index}/{total_videos})", "purple")
        write_log(f"\n[{index}/{total_videos}] Original: {raw_title}\n")
        ai_clean_title = clean_title_with_llama(raw_title, channel_name) # 🟢 ส่ง channel_name เข้าไปด้วย
        
        if use_popup:
            update_status("รอการยืนยันชื่อเพลง...", "#F57F17") 
            dialog = NameConfirmDialog(root, raw_title, ai_clean_title)
            
            if dialog.is_cancelled:
                write_log(f"⚠️ ยกเลิกการดาวน์โหลดเพลง: {raw_title}\n")
                continue  
                
            final_title = dialog.result
        else:
            final_title = ai_clean_title

        final_title = "".join(c for c in final_title if c not in r'<>:"/\|?*').strip()
        write_log(f"Confirmed Name: {final_title}\n")
        
        update_status(f"กำลังดาวน์โหลด... ({index}/{total_videos})", "blue")
        
        dl_command = [
            "yt-dlp", "-x", "--audio-format", "mp3",
            "-o", f"{final_title}.%(ext)s",  
            "--add-metadata", "--embed-thumbnail", "--newline",
            f"https://www.youtube.com/watch?v={vid}"
        ]
        
        try:
            process = subprocess.Popen(
                dl_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                text=True, bufsize=1, universal_newlines=True
            )

            for line in process.stdout:
                clean_line = process_log_line(line)
                if clean_line:
                    write_log(clean_line)

            process.wait()

            if process.returncode == 0:
                mp3_filepath = os.path.join(DOWNLOAD_PATH, f"{final_title}.mp3")
                if os.path.exists(mp3_filepath):
                    # 🟢 ส่งชื่อ Playlist และ Channel เข้าไปเขียนเป็น Album/Artist สำรองด้วย
                    if apply_metadata_to_file(mp3_filepath, final_title, playlist_name, channel_name):
                        write_log(f"✅ Metadata: Title/Artist/Album อัปเดตเรียบร้อย!\n")
                else:
                    write_log(f"⚠️ ไม่พบไฟล์ MP3 เพื่อแก้ไข Metadata: {mp3_filepath}\n")

        except Exception as e:
            write_log(f"❌ Error downloading {final_title}: {e}\n")

    update_status("ดาวน์โหลดและเปลี่ยนชื่อสำเร็จ! (Success!)", "green")
    counter_label.config(text="เสร็จสิ้น! (Completed!)")
    progress_var.set(100)
    
    # ดึงชื่ออัลบั้มมาแสดงใน Popup สรุปผล
    sample_album = video_list[0][2] if video_list and video_list[0][2] != "NA" else "ไม่พบชื่ออัลบั้ม"
    messagebox.showinfo("Success", f"ทำงานเรียบร้อยจำนวน {total_videos} เพลง\nอัลบั้ม: {sample_album}\n\nไฟล์บันทึกอยู่ที่:\n{DOWNLOAD_PATH}")
    reset_ui()

def process_log_line(line):
    percent_match = re.search(r'\[download\]\s+(\d+\.\d+)%', line)
    if percent_match:
        progress_var.set(float(percent_match.group(1)))
        return None 
        
    if "[youtube]" in line: return None 
    elif "Destination:" in line and "[download]" in line: return "Downloading...\n"
    elif "[ExtractAudio]" in line: return "Converting to MP3...\n"
    elif "[Metadata]" in line or "[ThumbnailsConvertor]" in line: return "Applying metadata and cover art...\n"
    elif "Deleting original file" in line: return "Cleaning up temporary files...\n"
    elif "has already been downloaded" in line: return "File already exists, skipping...\n"
    elif "ERROR" in line.upper(): return f"Error: {line.strip()}\n"
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
root.title("Y2MP3 + Llama 3.1 AI Manager")
root.geometry("600x670")  
root.resizable(False, False)

tk.Label(root, text="วางลิงก์ YouTube (Video หรือ Playlist):", font=("Arial", 11)).pack(pady=(15, 5))
url_entry = tk.Entry(root, width=65, font=("Arial", 10))
url_entry.pack(pady=5)
url_entry.focus_set()

tk.Label(root, text="จำนวนเพลงที่ต้องการ (เว้นว่างไว้ถ้าจะโหลดทั้งหมด):", font=("Arial", 11)).pack(pady=(10, 5))
num_entry = tk.Entry(root, width=15, justify='center', font=("Arial", 10))
num_entry.insert(0, "")
num_entry.pack(pady=5)

popup_var = tk.BooleanVar(value=True)  
popup_check = tk.Checkbutton(root, text="ตรวจสอบและยืนยันชื่อเพลงก่อนดาวน์โหลด (Popup Confirm)", 
                             variable=popup_var, font=("Arial", 10), fg="#333333")
popup_check.pack(pady=5)

download_btn = tk.Button(root, text="ดึงข้อมูล วิเคราะห์ และดาวน์โหลด (Start)", command=start_download, 
                         bg="#E53935", fg="white", font=("Arial", 11, "bold"), padx=20, pady=5)
download_btn.pack(pady=10)

counter_label = tk.Label(root, text="รอการดาวน์โหลด... (Waiting...)", font=("Arial", 10, "bold"), fg="#0078D4")
counter_label.pack(pady=0)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=500, mode='determinate')
progress_bar.pack(pady=10)

log_frame = tk.Frame(root)
log_frame.pack(pady=5)
log_scrollbar = tk.Scrollbar(log_frame)
log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_box = tk.Text(log_frame, height=10, width=70, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 9), 
                  state=tk.DISABLED, yscrollcommand=log_scrollbar.set)
log_box.pack(side=tk.LEFT, fill=tk.BOTH)
log_scrollbar.config(command=log_box.yview)

status_label = tk.Label(root, text=f"พร้อมใช้งาน\n(บันทึกไฟล์ที่: {DOWNLOAD_PATH})", font=("Arial", 9), fg="#555555")
status_label.pack(pady=10)

root.mainloop()