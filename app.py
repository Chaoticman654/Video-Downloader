import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pytube import YouTube

app = FastAPI()
DOWNLOAD_PATH = "/tmp/downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class DownloadRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("static/index.html") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse(content="<h1>Video Downloader</h1><p>Check /docs</p>")

@app.post("/download")
async def download_video(request: DownloadRequest):
    try:
        yt = YouTube(request.url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not stream:
            raise Exception("No MP4 stream available")
        
        filename = stream.download(output_path=DOWNLOAD_PATH)
        return {"status": "success", "title": yt.title, "filename": os.path.basename(filename)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/files")
async def list_files():
    files = []
    try:
        for file in os.listdir(DOWNLOAD_PATH):
            if file.endswith('.mp4'):
                files.append({"name": file, "url": f"/download/{file}"})
    except: pass
    return {"files": files}

@app.get("/download/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(DOWNLOAD_PATH, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='video/mp4', filename=filename)
    raise HTTPException(status_code=404, "File not found")
