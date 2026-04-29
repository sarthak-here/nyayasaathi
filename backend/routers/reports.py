from fastapi import APIRouter, HTTPException

from backend.services.report_generator import generate_report, get_report_types_list, get_report_type_fields

router = APIRouter(tags=["Reports"])


@router.get("/api/report/types")
def report_types():
    return get_report_types_list()


@router.get("/api/report/fields/{report_type}")
def report_fields(report_type: str):
    data = get_report_type_fields(report_type)
    if not data:
        raise HTTPException(status_code=404, detail=f"Unknown report type: {report_type}")
    return data


@router.post("/api/report/generate")
def report_generate(payload: dict):
    report_type = payload.get("report_type")
    if not report_type:
        raise HTTPException(status_code=400, detail="report_type is required")
    try:
        return generate_report(report_type, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
