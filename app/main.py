from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.auth import init_auth_db
from app.db.sqlite_db import init_db
from app.core.config import BASE_DIR, STATIC_DIR

init_db()
init_auth_db()

app = FastAPI(title="TCE Universal Bid Comparison Engine")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(auth_router)
app.include_router(jobs_router)


@app.get("/")
def homepage():
    return FileResponse(BASE_DIR / "backend" / "static" / "index.html")
