from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .config import settings
from .api.routes import router
import os

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Serve frontend build if dist exists
dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../frontend/dist"))
if not os.path.exists(dist_path):
    dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))

if os.path.exists(dist_path):
    assets_path = os.path.join(dist_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            return None
        file_target = os.path.join(dist_path, full_path)
        if os.path.isfile(file_target):
            return FileResponse(file_target)
        return FileResponse(os.path.join(dist_path, "index.html"))

@app.on_event("startup")
async def startup_event():
    print(f"Starting {settings.APP_NAME} with model {settings.OLLAMA_MODEL}...")

@app.on_event("shutdown")
async def shutdown_event():
    print(f"Shutting down {settings.APP_NAME}...")
