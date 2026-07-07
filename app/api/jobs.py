from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import shutil
from uuid import uuid4
from typing import Optional
from pydantic import BaseModel

from app.db.sqlite_db import create_job, get_job, get_jobs, update_status
from app.core.config import UPLOAD_DIR, TEMPLATE_PATH
from engine.pipeline.orchestrator import run_bid_job
from engine.llm.ollama_client import call_ollama
from app.auth import require_auth
import threading

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/jobs")
def jobs(auth=Depends(require_auth)):
    return {"jobs": get_jobs()}


@router.post("/upload")
async def upload(files: list[UploadFile] = File(...), template: Optional[UploadFile] = File(None), auth=Depends(require_auth)):
    job_id = str(uuid4())
    saved_paths = []
    for upload in files:
        dest = UPLOAD_DIR / upload.filename
        with dest.open("wb") as out:
            shutil.copyfileobj(upload.file, out)
        saved_paths.append(str(dest))

    template_path = str(TEMPLATE_PATH)
    if template is not None:
        template_path = str(UPLOAD_DIR / (template.filename or f"{job_id}_template.xlsx"))
        with Path(template_path).open("wb") as out:
            shutil.copyfileobj(template.file, out)

    create_job(job_id, saved_paths, template_path)
    return {"job_id": job_id, "files": saved_paths, "template": template_path}


@router.post("/analyze")
def analyze(job_id: str, auth=Depends(require_auth)):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    update_status(job_id, "queued")
    thread = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
    thread.start()
    return {"job_id": job_id, "status": "queued"}


@router.get("/status/{job_id}")
def status(job_id: str, auth=Depends(require_auth)):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job_id,
        "status": job.get("status"),
        "output": job.get("output"),
        "download_url": f"/api/download/{job_id}" if job.get("output") else None,
    }


@router.get("/download/{job_id}")
def download(job_id: str, auth=Depends(require_auth)):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    output = job.get("output")
    if not output:
        raise HTTPException(status_code=404, detail="Output not ready")
    output_path = Path(output)
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")
    return FileResponse(output_path, filename=output_path.name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


class AssistantRequest(BaseModel):
    question: str


@router.post("/assistant")
def assistant(payload: AssistantRequest, auth=Depends(require_auth)):
    prompt = f"Answer this procurement assistant question concisely and help the user with bid analytics or supplier evaluation.\nQuestion: {payload.question}\nResponse:"
    answer = call_ollama(prompt, max_tokens=300)
    if not answer:
        raise HTTPException(status_code=500, detail="Assistant model did not return a response")
    return {"answer": answer}


def _run_job(job_id: str):
    job = get_job(job_id)
    if not job:
        return
    update_status(job_id, "running")
    try:
        files = __import__("json").loads(job["files"])
        result = run_bid_job(files, job.get("template") or str(TEMPLATE_PATH))
        update_status(job_id, "completed", result.get("output_file"))
    except Exception:
        update_status(job_id, "error")
