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

def cleanup_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

@app.post("/download/")
def download_media(url: str, background_tasks: BackgroundTasks):
    try:
        # پاکسازی فایل‌های قدیمی
        old_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*"))
        for f in old_files:
            try:
                os.remove(f)
            except:
                pass

        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
        
        # استفاده از yt-dlp با تنظیمات سازگار با اینستاگرام و اسپاتیفای
        command = [
            "yt-dlp",
            "--no-check-certificates",
            "--geo-bypass",
            "-o", output_template,
            url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"YT-DLP Error: {result.stderr}")
            raise HTTPException(status_code=400, detail=f"خطا در دانلود: {result.stderr}")
        
        files = os.listdir(DOWNLOAD_DIR)
        if not files:
            raise HTTPException(status_code=404, detail="فایلی پس از دانلود پیدا نشد.")
            
        latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in files], key=os.path.getctime)
        
        background_tasks.add_task(cleanup_file, latest_file)
        
        return FileResponse(
            latest_file, 
            media_type='application/octet-stream', 
            filename=os.path.basename(latest_file)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"status": "Server is running successfully!"}
