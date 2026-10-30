from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Query, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import anyio
import uvicorn
from typing import Optional, Any, List
from .services.crack_analyzer import analyze_crack
from .schemas import (
    AnalysisResponse,
    TwoPointCalibrationRequest,
    TwoPointCalibrationResponse,
    ProbeApertureRequest,
    ProbeApertureResponse,
    AssetCreate,
    AssetResponse,
    SurveySaveRequest,
    BatchAnalysisResponse,
    BatchAnalysisSummary
)
from .services.calibration_service import calibration_service
from .services.pdf_generator import pdf_generator
from .db.session import init_db, get_db
from .db.repository import SurveyRepository
import os
from datetime import datetime

# Initialize SQLite database schema
init_db()

app = FastAPI(
    title="CrackVision AI API",
    description="API for high-resolution crack detection & segmentation in civil infrastructure",
    version="2.5.0"
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

def safe_parse_int(val: Any) -> Optional[int]:
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in ["", "none", "null", "undefined", "nan"]:
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None

import math

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engine": "ultralytics-yolov8-seg",
        "calibration": "aruco-fiducial-ready"
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
    standard_code: Optional[str] = Form("ACI"),
    marker_size_mm: Optional[Any] = Form(50.0),
    manual_scale_mm_per_pixel: Optional[Any] = Form(None),
    # Building Profile & Age Context Inputs
    building_name: Optional[str] = Form(None),
    building_type: Optional[str] = Form("residential"),
    construction_year: Optional[Any] = Form(None),
    building_age_years: Optional[Any] = Form(None),
    age_verification: Optional[str] = Form("unknown"),
    inspection_date: Optional[str] = Form(None),
    structural_system: Optional[str] = Form("unknown"),
    structural_material: Optional[str] = Form("reinforced_concrete"),
    member_importance: Optional[str] = Form(None),
    repair_history: Optional[str] = Form(None),
    last_major_inspection_date: Optional[str] = Form(None),
    last_repair_date: Optional[str] = Form(None),
    previous_crack_repairs: Optional[str] = Form("unknown"),
    previous_water_leakage: Optional[Any] = Form(False),
    known_reinforcement_corrosion: Optional[Any] = Form(False),
    known_spalling_delamination: Optional[Any] = Form(False),
    known_settlement: Optional[Any] = Form(False),
    damaging_events: Optional[str] = Form("none"),
    maintenance_condition: Optional[str] = Form("unknown"),
    environmental_exposure: Optional[str] = Form(None),
    db: Session = Depends(get_db)
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
    marker_size_float = safe_parse_float(marker_size_mm) or 50.0
    manual_scale_float = safe_parse_float(manual_scale_mm_per_pixel)
    construction_year_int = safe_parse_int(construction_year)
    building_age_float = safe_parse_float(building_age_years)
    prev_leakage_bool = safe_parse_bool(previous_water_leakage)
    known_corrosion_bool = safe_parse_bool(known_reinforcement_corrosion)
    known_spalling_bool = safe_parse_bool(known_spalling_delamination)
    known_settlement_bool = safe_parse_bool(known_settlement)

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
            standard_code,
            marker_size_float,
            manual_scale_float,
            building_name,
            building_type,
            construction_year_int,
            building_age_float,
            age_verification,
            inspection_date,
            structural_system,
            structural_material,
            member_importance,
            repair_history,
            last_major_inspection_date,
            last_repair_date,
            previous_crack_repairs,
            prev_leakage_bool,
            known_corrosion_bool,
            known_spalling_bool,
            known_settlement_bool,
            damaging_events,
            maintenance_condition,
            environmental_exposure
        )
        try:
            SurveyRepository.save_survey(db, result)
        except Exception as dbe:
            print(f"Notice: survey auto-persist skipped or already saved: {dbe}")
        return result
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ANALYZE ERROR: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/calibrate/two-point", response_model=TwoPointCalibrationResponse)
async def calibrate_two_point(request: TwoPointCalibrationRequest):
    """
    Compute millimeter-per-pixel spatial scale from two points and known dimension.
    """
    try:
        p1 = (request.point1[0], request.point1[1])
        p2 = (request.point2[0], request.point2[1])
        result = calibration_service.compute_two_point_scale(
            p1, p2, request.reference_length_mm, request.image_width
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/calibrate/probe-aperture", response_model=ProbeApertureResponse)
async def probe_aperture(request: ProbeApertureRequest):
    """
    Sample localized crack width normal to crack fissure tangent at click coordinate.
    """
    try:
        click_pt = (request.click_point[0], request.click_point[1])
        result = calibration_service.sample_localized_aperture(
            request.polygon, click_pt, request.mm_per_pixel
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==========================================
# Phase 05: Multi-Image Batch Analysis (REQ-4.4)
# ==========================================
@app.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch_images(
    files: List[UploadFile] = File(...),
    member_type: Optional[str] = Form(None),
    element_criticality: Optional[str] = Form("primary"),
    proximity_to_supports: Optional[str] = Form("unspecified"),
    visible_spalling: Optional[Any] = Form(False),
    visible_corrosion: Optional[Any] = Form(False),
    standard_code: Optional[str] = Form("ACI"),
    marker_size_mm: Optional[Any] = Form(50.0),
    # Building & Asset Profile
    building_name: Optional[str] = Form(None),
    building_type: Optional[str] = Form("unspecified"),
    construction_year: Optional[Any] = Form(None),
    age_verification: Optional[str] = Form("unknown"),
    inspection_date: Optional[str] = Form(None),
    structural_system: Optional[str] = Form("unknown"),
    structural_material: Optional[str] = Form("reinforced_concrete"),
    maintenance_condition: Optional[str] = Form("regular"),
    environmental_exposure: Optional[str] = Form("indoor_dry"),
    previous_repairs: Optional[str] = Form("unknown"),
    water_leakage: Optional[Any] = Form(False),
    known_settlement: Optional[Any] = Form(False),
    damaging_event: Optional[Any] = Form(False),
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for batch inspection.")

    spalling_bool = safe_parse_bool(visible_spalling)
    corrosion_bool = safe_parse_bool(visible_corrosion)
    marker_size_float = safe_parse_float(marker_size_mm) or 50.0
    const_year_int = safe_parse_int(construction_year)
    leakage_bool = safe_parse_bool(water_leakage)
    settlement_bool = safe_parse_bool(known_settlement)
    damaging_bool = safe_parse_bool(damaging_event)

    results = []
    total_defects = 0
    cracks_detected = 0
    severities = []
    confs = []

    for file in files:
        contents = await file.read()
        res = await anyio.to_thread.run_sync(
            analyze_crack,
            contents,
            file.filename,
            member_type,
            element_criticality,
            proximity_to_supports,
            spalling_bool,
            corrosion_bool,
            None,
            "unknown",
            None,
            standard_code,
            marker_size_float,
            None,
            building_name,
            building_type,
            const_year_int,
            None,  # building_age_years
            age_verification,
            inspection_date,
            structural_system,
            structural_material,
            None,  # member_importance
            None,  # repair_history
            None,  # last_major_inspection_date
            None,  # last_repair_date
            previous_repairs,
            leakage_bool,
            corrosion_bool,
            spalling_bool,
            settlement_bool,
            "event" if damaging_bool else "none",
            maintenance_condition,
            environmental_exposure
        )
        results.append(res)

        # Auto-persist each survey in database
        try:
            SurveyRepository.save_survey(db, res)
        except Exception:
            pass

        if res.get("status") == "crack_detected":
            cracks_detected += 1
        total_defects += int(res.get("defect_count", 0))
        severities.append(str(res.get("severity", "low")).lower())
        confs.append(float(res.get("confidence", 0.0)))

    # Determine highest severity
    highest_severity = "low"
    if "high" in severities:
        highest_severity = "high"
    elif "medium" in severities:
        highest_severity = "medium"

    summary = BatchAnalysisSummary(
        total_images=len(files),
        cracks_detected=cracks_detected,
        no_cracks_detected=len(files) - cracks_detected,
        highest_severity=highest_severity,
        mean_confidence=float(round(sum(confs) / max(len(confs), 1), 1)),
        total_defects=total_defects
    )

    return BatchAnalysisResponse(summary=summary, results=results)

# ==========================================
# Phase 05: Persistent Database Endpoints (REQ-4.1, REQ-4.2)
# ==========================================
@app.get("/api/surveys")
def list_surveys(
    severity: Optional[str] = Query(None),
    standard_code: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List historical inspection survey records with severity and standard code filtering.
    """
    return SurveyRepository.list_surveys(
        db, severity=severity, standard_code=standard_code, limit=limit, offset=offset
    )

@app.post("/api/surveys")
def save_survey_record(
    payload: SurveySaveRequest,
    db: Session = Depends(get_db)
):
    """
    Persist or update an inspection survey record.
    """
    data = payload.model_dump()
    return SurveyRepository.save_survey(db, data, thumbnail_data=payload.thumbnail)

@app.get("/api/surveys/{survey_id}")
def get_survey_record(
    survey_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve full details for an inspection survey record.
    """
    survey = SurveyRepository.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    return survey

@app.delete("/api/surveys/{survey_id}")
def delete_survey_record(
    survey_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an inspection survey record.
    """
    deleted = SurveyRepository.delete_survey(db, survey_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    return {"status": "deleted", "survey_id": survey_id}

@app.get("/api/assets", response_model=List[AssetResponse])
def list_infrastructure_assets(db: Session = Depends(get_db)):
    """
    List all registered infrastructure assets.
    """
    return SurveyRepository.list_assets(db)

@app.post("/api/assets", response_model=AssetResponse)
def create_infrastructure_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new infrastructure asset.
    """
    return SurveyRepository.create_asset(
        db,
        asset_tag=payload.asset_tag,
        name=payload.name,
        component_type=payload.component_type,
        location=payload.location
    )

# ==========================================
# Phase 05: Server-Side PDF Export (REQ-4.3)
# ==========================================
@app.get("/api/surveys/{survey_id}/pdf")
def download_survey_pdf(
    survey_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate and download official Structural Condition Assessment Report (SCAR) PDF.
    """
    survey = SurveyRepository.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")

    pdf_bytes = pdf_generator.generate_scar_pdf(survey)
    filename = f"SCAR_Report_{survey_id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/pdf"
        }
    )

@app.post("/api/surveys/export-pdf")
def export_survey_pdf_direct(payload: SurveySaveRequest):
    """
    Generate and download official SCAR PDF directly from client-side state.
    """
    data = payload.model_dump()
    survey_id = data.get("survey_id") or data.get("analysis_id", "UNSAVED")
    pdf_bytes = pdf_generator.generate_scar_pdf(data)
    filename = f"SCAR_Report_{survey_id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/pdf"
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
