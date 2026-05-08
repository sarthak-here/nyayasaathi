import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.services.agent_singleton import agent
from backend.services.letter_generator import generate_letter_stream

router = APIRouter(tags=["Legal"])


class AnalyzeRequest(BaseModel):
    situation: str
    language: str = "auto"


class LetterRequest(BaseModel):
    situation: str
    language: str = "auto"
    user_name: str
    user_address: str
    user_phone: str = ""
    respondent: str
    respondent_address: str = ""


class TranscribeRequest(BaseModel):
    audio_path: str


@router.get("/api/health")
def health():
    import os
    return {"status": "ok", "model": os.getenv("OLLAMA_MODEL", "gemma4:e2b")}


@router.post("/api/analyze/stream")
async def analyze_stream(req: AnalyzeRequest):
    from backend.services.legal_agent import extract_json

    def event_stream():
        full_response = ""
        try:
            for token in agent.analyze_stream(req.situation, language=req.language):
                full_response += token
                yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"
            result = extract_json(full_response)
            yield f"data: {json.dumps({'type': 'result', 'data': result})}\n\n"
            yield "data: {\"type\": \"done\"}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    try:
        return agent.analyze(req.situation, language=req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/letter/stream")
async def letter_stream(req: LetterRequest):
    def event_stream():
        try:
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
                yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'full_text': letter_text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.post("/api/transcribe")
def transcribe(req: TranscribeRequest):
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(req.audio_path)
        return {"text": result["text"].strip()}
    except ImportError:
        raise HTTPException(status_code=501,
                            detail="Voice input requires openai-whisper. Run: pip install openai-whisper")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
