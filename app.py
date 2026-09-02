import json
import os
import shutil
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from core.pipeline import process_video

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")

INPUT = BASE / "input"
OUTPUT = BASE / "output"
INPUT.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "500")) * 1024 * 1024

app = FastAPI(title="AI Clipping Automation MVP", version="1.1.0")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


def safe_job_id(job_id: str) -> bool:
    return len(job_id) == 12 and all(c in "0123456789abcdef" for c in job_id)


@app.get("/")
def home():
    return FileResponse(BASE / "static/index.html")


@app.get("/api/health")
def health():
    ffmpeg_ok = shutil.which("ffmpeg") is not None
    ffprobe_ok = shutil.which("ffprobe") is not None
    return {
        "ok": True,
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "ffmpeg_available": ffmpeg_ok,
        "ffprobe_available": ffprobe_ok,
        "max_upload_mb": MAX_UPLOAD_BYTES // 1024 // 1024,
    }


@app.post("/api/process")
async def process(background_tasks: BackgroundTasks, video: UploadFile = File(...)):
    if not video.filename:
        raise HTTPException(400, "Please choose a video file.")

    suffix = Path(video.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Supported video types: MP4, MOV, MKV, WEBM.")

    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(503, "GROQ_API_KEY is not configured yet.")
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise HTTPException(503, "FFmpeg/ffprobe is not installed in this environment.")

    job = uuid.uuid4().hex[:12]
    src = INPUT / f"{job}{suffix}"
    out_dir = OUTPUT / job
    total = 0

    try:
        with src.open("wb") as f:
            while True:
                chunk = await video.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    raise HTTPException(413, f"Video is too large. Maximum is {MAX_UPLOAD_BYTES // 1024 // 1024} MB.")
                f.write(chunk)
    except HTTPException:
        src.unlink(missing_ok=True)
        raise
    except Exception as exc:
        src.unlink(missing_ok=True)
        raise HTTPException(500, f"Could not save the uploaded video: {exc}")
    finally:
        await video.close()

    background_tasks.add_task(process_video, str(src), str(out_dir))
    return {"job_id": job, "status": "queued", "message": "Processing started."}


@app.get("/api/jobs/{job_id}")
def status(job_id: str):
    if not safe_job_id(job_id):
        raise HTTPException(400, "Invalid job ID.")

    d = OUTPUT / job_id
    if not d.exists():
        return {"job_id": job_id, "status": "queued"}

    error_file = d / "error.json"
    done_file = d / "done.json"
    if error_file.exists():
        return {"job_id": job_id, "status": "error", **json.loads(error_file.read_text(encoding="utf-8"))}
    if done_file.exists():
        data = json.loads(done_file.read_text(encoding="utf-8"))
        data["status"] = "done"
        data["job_id"] = job_id
        return data
    return {"job_id": job_id, "status": "processing"}


@app.get("/api/jobs/{job_id}/files")
def files(job_id: str):
    if not safe_job_id(job_id):
        raise HTTPException(400, "Invalid job ID.")
    d = OUTPUT / job_id
    if not d.exists():
        raise HTTPException(404, "Job not found")
    return {"files": [p.name for p in sorted(d.glob("*.mp4"))]}


@app.get("/api/jobs/{job_id}/download/{filename}")
def download(job_id: str, filename: str):
    if not safe_job_id(job_id):
        raise HTTPException(400, "Invalid job ID.")
    job_dir = (OUTPUT / job_id).resolve()
    p = (job_dir / Path(filename).name).resolve()
    if p.parent != job_dir or p.suffix.lower() != ".mp4" or not p.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(p, media_type="video/mp4", filename=p.name)
