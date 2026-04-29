import io
import re
import json
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.services.itr_advisor import full_itr_analysis

router = APIRouter(tags=["ITR"])


class ITRRequest(BaseModel):
    name: str = ""
    pan: str = ""
    assessment_year: str = "2025-26"
    salary_income: float = 0
    business_income: float = 0
    capital_gains: float = 0
    other_income: float = 0
    deduction_80c: float = 0
    deduction_80d: float = 0
    deduction_80g: float = 0
    deduction_80ccd1b: float = 0
    deduction_80e: float = 0
    deduction_80tta: float = 0
    deduction_80eea: float = 0
    deduction_80gg: float = 0
    hra_exempt: float = 0
    home_loan_interest: float = 0
    presumptive_business: bool = False
    foreign_income: bool = False
    house_properties: int = 1


@router.post("/api/itr/analyze")
def itr_analyze(req: ITRRequest):
    try:
        return full_itr_analysis(req.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/parse-statement")
async def parse_statement(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        import pypdf
        contents = await file.read()
        reader = pypdf.PdfReader(io.BytesIO(contents))
        full_text = "\n".join(page.extract_text() or "" for page in reader.pages)

        entries = []
        total_credit = 0.0
        tx_pattern = re.compile(
            r"(\d{2}[-/]\d{2}[-/]\d{2,4})\s+"
            r"(.+?)\s+"
            r"([\d,]+\.\d{2})\s+"
            r"([\d,]+\.\d{2})?\s*"
            r"([\d,]+\.\d{2})"
        )
        for line in full_text.split("\n"):
            m = tx_pattern.search(line)
            if not m:
                continue
            date, narration, amt1, amt2, balance = m.groups()
            narration = narration.strip()
            line_lower = line.lower()
            is_credit = any(k in line_lower for k in ["cr", "credit", "deposit", "salary", "neft cr", "interest", "reversal", "cash dep"])
            is_debit  = any(k in line_lower for k in ["dr", "debit", "withdrawal", "atm", "pos", "nach dr", "upi"])
            credit = debit = 0.0
            val = float(amt1.replace(",", ""))
            if is_credit and not is_debit:
                credit = val
            elif is_debit and not is_credit:
                debit = val
            else:
                credit = val
            total_credit += credit
            entries.append({
                "date": date,
                "narration": narration,
                "credit": round(credit, 2),
                "debit": round(debit, 2),
                "balance": balance,
            })

        return JSONResponse({
            "entries": entries[:50],
            "total_credit": round(total_credit, 2),
            "total_entries": len(entries),
            "raw_text_preview": full_text[:500],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not parse PDF: {e}")
