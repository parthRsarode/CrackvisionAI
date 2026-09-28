from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import anyio
import uvicorn
from typing import Optional, Any
from .services.crack_analyzer import analyze_crack
from .schemas import AnalysisResponse
import os
from datetime import datetime

app = FastAPI(
    title="CrackVision AI API",
    description="API for high-resolution crack detection & segmentation in civil infrastructure",
    version="2.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def safe_parse_bool(val: Any) -> bool:
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in ["true", "1", "yes", "on"]

def safe_parse_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in ["", "none", "null", "undefined", "nan"]:
        return None
    try:
        f = float(s)
        return None if math.isnan(f) else f
    except (ValueError, TypeError):
        return None

import math

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engine": "ultralytics-yolov8-seg"
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    member_type: Optional[str] = Form(None),
    element_criticality: Optional[str] = Form("primary"),
    proximity_to_supports: Optional[str] = Form("unspecified"),
    visible_spalling: Optional[Any] = Form(False),
    visible_corrosion: Optional[Any] = Form(False),
    previous_width_mm: Optional[Any] = Form(None),
    crack_depth_status: Optional[str] = Form("unknown"),
    environment: Optional[str] = Form(None),
    standard_code: Optional[str] = Form("ACI")
):
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        # Fallback check extension if content_type header is generic
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            )
    
    contents = await file.read()
    if len(contents) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 15MB"
        )
    
    await file.seek(0)
    
    spalling_bool = safe_parse_bool(visible_spalling)
    corrosion_bool = safe_parse_bool(visible_corrosion)
    prev_width_float = safe_parse_float(previous_width_mm)

    try:
        result = await anyio.to_thread.run_sync(
            analyze_crack,
            contents,
            file.filename,
            member_type,
            element_criticality,
            proximity_to_supports,
            spalling_bool,
            corrosion_bool,
            prev_width_float,
            crack_depth_status,
            environment,
            standard_code
        )
        return result
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ANALYZE ERROR: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
