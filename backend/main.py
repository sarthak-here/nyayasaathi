"""
NyayaSaathi — FastAPI Backend
Run: uvicorn backend.main:app --reload --port 8000
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.services.agent_singleton import agent
from backend.routers import legal, itr, reports, documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[NyayaSaathi] Loading embedding model and ChromaDB... ", end="", flush=True)
    agent._init_db()
    print("ready.")
    yield


app = FastAPI(
    title="NyayaSaathi API",
    description="Free Legal Assistant for India — Powered by Gemma 4 (Offline)",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(legal.router)
app.include_router(itr.router)
app.include_router(reports.router)
app.include_router(documents.router)

frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
