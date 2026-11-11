from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import glob

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# تابعی برای پاک کردن امن فایل بعد از ارسال به کاربر
def cleanup_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File deleted: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")

@app.post("/download/")
def download_media(url: str, background_tasks: BackgroundTasks):
    try:
        # پاکسازی فایل‌های باقی‌مانده احتمالی از قبل
        old_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*"))
        for f in old_files:
            try:
                os.remove(f)
            except:
                pass

        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
        
        # دانلود با yt-dlp
        command = ["yt-dlp", "-o", output_template, url]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise HTTPException(status_code=400, detail="خطا در دانلود لینک. لطفاً لینک معتبر وارد کنید.")
        
        # پیدا کردن فایل دانلود شده جدید
        files = os.listdir(DOWNLOAD_DIR)
        if not files:
            raise HTTPException(status_code=404, detail="فایلی پیدا نشد.")
            
        latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in files], key=os.path.getctime)
        
        # اضافه کردن کار پاکسازی به پس‌زمینه (بعد از اینکه فایل کامل فرستاده شد، پاک می‌شود)
        background_tasks.add_task(cleanup_file, latest_file)
        
        return FileResponse(
            latest_file, 
            media_type='application/octet-stream', 
            filename=os.path.basename(latest_file)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
