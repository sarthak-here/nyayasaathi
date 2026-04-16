"""
NyayaSaathi — FastAPI Backend
Exposes the legal agent, letter generator, and PDF export as REST endpoints.
Run: uvicorn api.server:app --reload --port 8000
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.legal_agent import LegalAgent, extract_json
from core.letter_generator import generate_letter_stream, generate_letter
from core.pdf_export import export_to_pdf

app = FastAPI(
    title="NyayaSaathi API",
    description="Free Legal Assistant for India — Powered by Gemma 4 (Offline)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = LegalAgent()

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    situation: str
    language: str = "auto"  # auto | english | hindi | hinglish


class LetterRequest(BaseModel):
    situation: str
    language: str = "auto"
    user_name: str
    user_address: str
    user_phone: str = ""
    respondent: str
    respondent_address: str = ""


class PDFRequest(BaseModel):
    letter_text: str
    user_name: str = "Complainant"


class TranscribeRequest(BaseModel):
    audio_path: str


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "model": os.getenv("OLLAMA_MODEL", "gemma4:e2b")}


# ---------------------------------------------------------------------------
# Analyze — streaming SSE
# ---------------------------------------------------------------------------

@app.post("/api/analyze/stream")
async def analyze_stream(req: AnalyzeRequest):
    """Stream legal analysis as Server-Sent Events."""

    def event_stream():
        full_response = ""
        try:
            for token in agent.analyze_stream(req.situation, language=req.language):
                full_response += token
                data = json.dumps({"type": "token", "text": token})
                yield f"data: {data}\n\n"

            # Parse final result
            result = extract_json(full_response)
            if isinstance(result.get("recommended_action"), list):
                result["recommended_action"] = result["recommended_action"]
            data = json.dumps({"type": "result", "data": result})
            yield f"data: {data}\n\n"
            yield "data: {\"type\": \"done\"}\n\n"

        except Exception as e:
            data = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    """Non-streaming legal analysis."""
    try:
        result = agent.analyze(req.situation, language=req.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Letter generation — streaming SSE
# ---------------------------------------------------------------------------

@app.post("/api/letter/stream")
async def letter_stream(req: LetterRequest):
    """Stream complaint letter generation as Server-Sent Events."""

    def event_stream():
        try:
            # Get analysis for context
            analysis = agent.analyze(req.situation, language=req.language)

            letter_text = ""
            for token in generate_letter_stream(
                situation=req.situation,
                user_name=req.user_name,
                user_address=req.user_address,
                user_phone=req.user_phone or "Not provided",
                respondent=req.respondent,
                respondent_address=req.respondent_address or "Address not known",
                legal_analysis=analysis,
            ):
                letter_text += token
                data = json.dumps({"type": "token", "text": token})
                yield f"data: {data}\n\n"

            data = json.dumps({"type": "done", "full_text": letter_text})
            yield f"data: {data}\n\n"

        except Exception as e:
            data = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# PDF Export
# ---------------------------------------------------------------------------

@app.post("/api/pdf")
def generate_pdf(req: PDFRequest):
    """Export letter text to PDF and return it as a downloadable file."""
    if not req.letter_text.strip():
        raise HTTPException(status_code=400, detail="Letter text is empty")
    try:
        pdf_path = export_to_pdf(req.letter_text, user_name=req.user_name)
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"NyayaSaathi_Letter_{req.user_name.replace(' ', '_')}.pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Voice transcription
# ---------------------------------------------------------------------------

@app.post("/api/transcribe")
def transcribe(req: TranscribeRequest):
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(req.audio_path)
        return {"text": result["text"].strip()}
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Voice input requires openai-whisper. Run: pip install openai-whisper",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Serve frontend (static files)
# ---------------------------------------------------------------------------

frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
