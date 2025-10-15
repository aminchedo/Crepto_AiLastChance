"""
Export API for BOLT AI Neural Agent System
"""

from typing import Any, Dict

import pandas as pd
from fastapi import APIRouter, HTTPException
from services.export.export_service import get_export_service

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/csv")
async def export_csv(name: str, data: Dict[str, Any]):
    try:
        df = pd.DataFrame(data)
        path = get_export_service().export_csv(df, name)
        return {"status": "ok", "file": str(path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/excel")
async def export_excel(name: str, data: Dict[str, Any]):
    try:
        df = pd.DataFrame(data)
        path = get_export_service().export_excel(df, name)
        return {"status": "ok", "file": str(path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/json")
async def export_json(name: str, data: Any):
    try:
        path = get_export_service().export_json(data, name)
        return {"status": "ok", "file": str(path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pdf")
async def export_pdf(name: str, html: str):
    try:
        path = get_export_service().generate_pdf_report(html, name)
        if not path:
            return {"status": "skipped", "message": "weasyprint not installed"}
        return {"status": "ok", "file": str(path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
