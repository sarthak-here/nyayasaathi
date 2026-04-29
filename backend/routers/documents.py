from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.services.pdf_export import export_to_pdf

router = APIRouter(tags=["Documents"])


class PDFRequest(BaseModel):
    letter_text: str
    user_name: str = "Complainant"


@router.post("/api/pdf")
def generate_pdf(req: PDFRequest):
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
