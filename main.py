import os
import time
import shutil
import threading
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp

app = FastAPI()

# CORS settings for Hostinger Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # अपनी Hostinger URL यहाँ डालें
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- Auto Delete Logic ---
def cleanup_files():
    while True:
        now = time.time()
        for f in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, f)
            # अगर फाइल 3 मिनट (180 seconds) से पुरानी है तो डिलीट करें
            if os.stat(file_path).st_mtime < now - 180:
                if os.path.isfile(file_path):
                    os.remove(file_path)
        time.sleep(60) # हर 1 मिनट में चेक करेगा

# बैकग्राउंड थ्रेड शुरू करें
threading.Thread(target=cleanup_files, daemon=True).start()

@app.get("/")
def home():
    return {"message": "Instagram Downloader API is Running!"}

@app.get("/download")
async def download_video(url: str):
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        return {"download_url": f"https://YOUR-RENDER-APP-URL.onrender.com/get-file?path={os.path.basename(filename)}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get-file")
async def get_file(path: str):
    file_full_path = os.path.join(DOWNLOAD_DIR, path)
    if os.path.exists(file_full_path):
        return FileResponse(file_full_path)
    return {"error": "File expired or not found"}
