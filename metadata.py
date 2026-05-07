import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

try:
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3NoHeaderError, ID3, TIT2, TPE1
except ImportError:
    messagebox.showerror("Error", "กรุณาติดตั้งไลบรารีก่อนรันโปรแกรม:\npip install mutagen")
    exit()

def start_fixing():
    folder_path = path_entry.get().strip()
    if not os.path.exists(folder_path):
        messagebox.showwarning("Warning", "ไม่พบโฟลเดอร์ที่ระบุ")
        return
        
    start_btn.config(state=tk.DISABLED)
    threading.Thread(target=process_files, args=(folder_path,), daemon=True).start()

def process_files(folder_path):
    mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]
    total_files = len(mp3_files)

    if total_files == 0:
        messagebox.showinfo("Info", "ไม่พบไฟล์ MP3 ในโฟลเดอร์นี้")
        reset_ui()
        return

    clear_log()
    write_log(f"🔍 พบไฟล์ MP3 ทั้งหมด {total_files} ไฟล์\nกำลังเริ่มแก้ไข Metadata โดยยึดจากชื่อไฟล์...\n{'-'*50}\n")
    
    success_count = 0
    for i, filename in enumerate(mp3_files):
        # 🟢 1. เช็คและเปลี่ยนชื่อไฟล์ (Rename) จาก แหลม สมพล -> LHAM SOMPHOL
        if "แหลม สมพล" in filename:
            new_filename = filename.replace("แหลม สมพล", "LHAM SOMPHOL")
            old_filepath = os.path.join(folder_path, filename)
            new_filepath = os.path.join(folder_path, new_filename)
            
            try:
                os.rename(old_filepath, new_filepath)
                write_log(f"🔄 เปลี่ยนชื่อไฟล์: {filename} -> {new_filename}\n")
                filename = new_filename # อัปเดตตัวแปร filename เป็นชื่อใหม่เพื่อใช้งานต่อ
            except Exception as e:
                write_log(f"❌ Error เปลี่ยนชื่อไฟล์ {filename}: {e}\n")

        # 🟢 2. ดำเนินการแยกชื่อและแก้ไข Metadata ตามปกติ
        filepath = os.path.join(folder_path, filename)
        name_without_ext = os.path.splitext(filename)[0]

        # หั่นชื่อไฟล์ด้วย " - "
        parts = name_without_ext.split(" - ")

        if len(parts) >= 2:
            # สมมติฐาน: Song - Artist
            # กรณีมีขีดมากกว่า 1 ตัว ให้ถือว่าอันสุดท้ายคือตัวแบ่งระหว่าง เพลง กับ ศิลปิน
            artist = parts[-1].strip()
            title = " - ".join(parts[:-1]).strip()

            try:
                # พยายามเปิดไฟล์เพื่อแก้ Metadata
                try:
                    audio = EasyID3(filepath)
                except ID3NoHeaderError:
                    # ถ้าไฟล์ไม่เคยมี Metadata มาก่อนเลย ให้สร้างใหม่
                    meta = ID3()
                    meta.save(filepath)
                    audio = EasyID3(filepath)

                # บันทึก Title และ Artist ลงไปในไฟล์
                audio['title'] = title
                audio['artist'] = artist
                
                # ล้างข้อมูลขยะอื่นๆ ออก (ถ้ามี)
                if 'album' in audio: audio['album'] = ''
                if 'comment' in audio: audio['comment'] = ''
                
                audio.save()

                write_log(f"✅ {filename}\n   ↳ Title: {title} | Artist: {artist}\n")
                success_count += 1
            except Exception as e:
                write_log(f"❌ Error แก้ไขไฟล์ {filename}: {e}\n")
        else:
            write_log(f"⚠️ ข้าม {filename}: รูปแบบชื่อไม่ตรงเงื่อนไข (ไม่พบ ' - ')\n")

        # อัปเดต Progress Bar
        progress_var.set(((i + 1) / total_files) * 100)
        root.update_idletasks()

    write_log(f"{'-'*50}\n🎉 เสร็จสิ้น! แก้ไขสำเร็จ {success_count}/{total_files} ไฟล์")
    messagebox.showinfo("Success", f"แก้ไข Metadata สำเร็จจำนวน {success_count} ไฟล์!")
    reset_ui()

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, folder_selected)

def write_log(text):
    log_box.config(state=tk.NORMAL)
    log_box.insert(tk.END, text)
    log_box.see(tk.END)
    log_box.config(state=tk.DISABLED)

def clear_log():
    log_box.config(state=tk.NORMAL)
    log_box.delete(1.0, tk.END)
    log_box.config(state=tk.DISABLED)

def reset_ui():
    start_btn.config(state=tk.NORMAL)
    progress_var.set(0)

# --- GUI Setup ---
root = tk.Tk()
root.title("MP3 Metadata Fixer (Song - Artist)")
root.geometry("550x450")
root.resizable(False, False)

tk.Label(root, text="เลือกโฟลเดอร์ที่มีไฟล์ MP3:", font=("Arial", 11, "bold")).pack(pady=(15, 5))

path_frame = tk.Frame(root)
path_frame.pack(pady=5)

# ค่าเริ่มต้นเป็นโฟลเดอร์ Music ของเครื่อง
default_path = os.path.join(os.path.expanduser("~"), "Music")
path_entry = tk.Entry(path_frame, width=50, font=("Arial", 10))
path_entry.insert(0, default_path)
path_entry.pack(side=tk.LEFT, padx=(0, 5))

tk.Button(path_frame, text="Browse...", command=browse_folder).pack(side=tk.LEFT)

start_btn = tk.Button(root, text="เริ่มแก้ไข Metadata (Start)", command=start_fixing, 
                      bg="#1976D2", fg="white", font=("Arial", 11, "bold"), padx=15, pady=5)
start_btn.pack(pady=15)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=480, mode='determinate')
progress_bar.pack(pady=5)

log_frame = tk.Frame(root)
log_frame.pack(pady=10)
log_scrollbar = tk.Scrollbar(log_frame)
log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_box = tk.Text(log_frame, height=12, width=65, bg="#1E1E1E", fg="#4CAF50", font=("Consolas", 9), 
                  state=tk.DISABLED, yscrollcommand=log_scrollbar.set)
log_box.pack(side=tk.LEFT, fill=tk.BOTH)
log_scrollbar.config(command=log_box.yview)

root.mainloop()