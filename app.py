import os
import yt_dlp
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Video Downloader")

# Render config
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', '/tmp/downloads')
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class DownloadRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.post("/download")
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks):
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'format': 'best[height<=720]',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            title = info.get('title', 'video')
            
            def download():
                ydl.download([request.url])
            
            background_tasks.add_task(download)
        
        return {
            "status": "started",
            "title": title,
            "message": "Download started! Check /files",
            "files_url": "/files"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/files")
async def list_files():
    files = []
    try:
        for file in os.listdir(DOWNLOAD_PATH):
            if file.endswith(('.mp4', '.mkv', '.webm', '.mp3')):
                size = os.path.getsize(os.path.join(DOWNLOAD_PATH, file)) / (1024*1024)  # MB
                files.append({
                    "name": file, 
                    "size_mb": round(size, 1),
                    "url": f"/download/{file}"
                })
    except:
        pass
    return {"files": files, "download_path": DOWNLOAD_PATH}

@app.get("/download/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(DOWNLOAD_PATH, filename)
    if os.path.exists(file_path):
        return FileResponse(
            file_path, 
            media_type='video/mp4', 
            filename=filename,
            headers={"Accept-Ranges": "bytes"}
        )
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 8000)))
