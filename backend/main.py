from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from pathlib import Path
import shutil
import threading
import logging
from engine import run_bid_analysis
from database.sqlite_db import init_db, create_job, update_status, get_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
TEMPLATE_PATH = BASE_DIR / "templates" / "template.xlsx"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
init_db()

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def homepage():
    return FileResponse(BASE_DIR / "frontend" / "index.html")


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    job_id = str(uuid4())
    saved_paths = []
    for f in files:
        dest = UPLOAD_DIR / f.filename
        with dest.open("wb") as out:
            shutil.copyfileobj(f.file, out)
        saved_paths.append(str(dest))
    # create job entry without template yet
    create_job(job_id, saved_paths, "")
    return {"job_id": job_id, "files": saved_paths}


def _run_job(job_id: str):
    job = get_job(job_id)
    if not job:
        return
    update_status(job_id, "running")
    files = []
    try:
        files = __import__("json").loads(job["files"])
    except Exception:
        files = []

    template = job.get("template") or str(TEMPLATE_PATH)
    try:
        res = run_bid_analysis(files, template)
        update_status(job_id, "completed", res.get("output_file"))
    except Exception as e:
        update_status(job_id, "error")


@app.post("/analyze")
def analyze(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    update_status(job_id, "queued")
    thread = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
    thread.start()
    return {"job_id": job_id}


@app.get("/status/{job_id}")
def status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    download_url = None
    output_path = job.get("output")
    if output_path:
        download_url = f"/download/{job_id}"

    return {
        "id": job_id,
        "status": job.get("status"),
        "output": output_path,
        "download_url": download_url,
    }


@app.get("/download/{job_id}")
def download(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    out = job.get("output")
    if not out:
        raise HTTPException(status_code=404, detail="Output not ready")
    return FileResponse(out, filename=Path(out).name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
