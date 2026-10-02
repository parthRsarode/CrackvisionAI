from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class CalibrationInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    calibration_status: str = Field(default="uncalibrated_macro", description="fiducial_calibrated | user_two_point_calibrated | uncalibrated_macro")
    method: str = Field(default="default_macro", description="aruco_fiducial | manual_two_point | default_macro")
    marker_id: Optional[int] = Field(default=None, description="Detected ArUco ID if applicable")
    marker_size_mm: Optional[float] = Field(default=50.0, description="Known physical dimension of fiducial marker")
    mean_side_px: float = Field(default=0.0, description="Mean detected side length in pixels")
    marker_corners: List[List[float]] = Field(default_factory=list, description="Pixel corners of detected marker [[x, y], ...]")
    normalized_corners: List[List[float]] = Field(default_factory=list, description="Normalized 0-1 corners")
    mm_per_pixel: float = Field(default=0.234, description="Calibrated millimeter to pixel scale factor")
    assumed_field_width_m: float = Field(default=0.15, description="Effective physical field of view in meters")
    confidence: float = Field(default=0.0, description="Fiducial detection confidence")

class TwoPointCalibrationRequest(BaseModel):
    point1: List[float] = Field(..., description="[x1, y1] coordinates")
    point2: List[float] = Field(..., description="[x2, y2] coordinates")
    reference_length_mm: float = Field(..., description="Known distance in millimeters")
    image_width: int = Field(default=640, description="Image width in pixels")

class TwoPointCalibrationResponse(BaseModel):
    calibration_status: str
    method: str
    pixel_distance: float
    reference_length_mm: float
    mm_per_pixel: float
    assumed_field_width_m: float

class ProbeApertureRequest(BaseModel):
    polygon: List[List[float]] = Field(..., description="Polygon coordinates [[x, y], ...]")
    click_point: List[float] = Field(..., description="[x, y] coordinates of inspection point")
    mm_per_pixel: float = Field(default=0.234, description="Current scale factor")

class ProbeApertureResponse(BaseModel):
    width_px: float
    width_mm: float
    span_points: List[List[float]]

class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: str
    status: str  # "crack_detected" or "no_significant_crack"
    confidence: float  # percentage 0-100
    crack_type: str
    severity: str  # "low", "medium", "high"
    estimated_width: str  # e.g., "0.3 - 0.7 mm"
    affected_area: str  # e.g., "4.8%"
    recommendation: str
    inspection_note: str
    annotated_image_note: str
    created_at: datetime

    # Phase 03 Computer Vision Segmentation Fields
    has_segmentation: bool = Field(default=False, description="True if real YOLOv8 segmentation was executed")
    polygons: List[List[List[float]]] = Field(default_factory=list, description="Pixel coordinate polygons [[x, y], ...]")
    normalized_polygons: List[List[List[float]]] = Field(default_factory=list, description="Normalized 0-1 polygons [[x/w, y/h], ...]")
    bounding_boxes: List[List[float]] = Field(default_factory=list, description="Bounding boxes [[x1, y1, x2, y2], ...]")
    defect_count: int = Field(default=0, description="Total number of distinct crack fissures detected")
    inference_time_ms: float = Field(default=0.0, description="Inference latency in milliseconds")
    aci_compliance: Optional[Dict[str, Any]] = Field(default=None, description="ACI 224R-01 permissible limit compliance")
    calibration: Optional[CalibrationInfo] = Field(default=None, description="Optical calibration scale and fiducial data")

    # Section 1-8 Refined Engineering & Assessment Fields
    crack_depth_status: str = Field(
        default="unknown",
        description="Crack depth state: not_assessed | unknown | surface_only | measured_externally | further_investigation_required"
    )
    crack_depth_explanation: str = Field(
        default="Crack depth cannot be established from surface optical images alone.",
        description="Explicit note regarding surface optical limitation and lack of internal depth data."
    )
    evidence_sufficiency: Dict[str, Any] = Field(
        default_factory=lambda: {
            "status": "insufficient_for_engineering_assessment",
            "missing_factors": ["internal_crack_depth", "optical_calibration_target"],
            "summary": "Evidence is sufficient for surface anomaly detection, but additional context is required for structural engineering verification."
        },
        description="Assessment of whether current data is sufficient for full engineering verdict."
    )
    assessment_breakdown: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured multi-factor observation breakdown (Observation, Structural Context, Deterioration, Engineering Assessment)."
    )
    compliance_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Explainable standards status (verified | provisionally_consistent | requires_review | potential_non_conformance | unable_to_determine)."
    )
    plain_language_explanation: str = Field(
        default="",
        description="Layperson explanation translating technical metrics for non-engineers."
    )
    multi_factor_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed metrics: width, length, area, density, orientation, pattern, spacing, proximity, spalling, corrosion, history."
    )
    unsupported_claims_disclaimer: str = Field(
        default="Surface condition appears consistent with selected criteria, but overall structural safety cannot be established from image analysis alone.",
        description="Engineering safety disclaimer preventing absolute claims of structural safety."
    )

class AssetCreate(BaseModel):
    asset_tag: str = Field(..., description="Unique tag e.g. BR-104-N")
    name: str = Field(..., description="Descriptive asset name")
    component_type: str = Field(default="Structural Concrete", description="Element type")
    location: str = Field(default="Field Site", description="Physical location")

class AssetResponse(BaseModel):
    id: int
    asset_tag: str
    name: str
    component_type: str
    location: str
    survey_count: int = 0
    created_at: Optional[str] = None

class SurveySaveRequest(BaseModel):
    survey_id: Optional[str] = None
    analysis_id: Optional[str] = None
    asset_id: Optional[int] = None
    filename: Optional[str] = "inspection.jpg"
    thumbnail: Optional[str] = None
    status: str = "crack_detected"
    severity: str = "low"
    confidence: float = 0.0
    crack_type: str = "None"
    estimated_width: str = "0.0 mm"
    max_aperture_mm: Optional[float] = 0.0
    affected_area: str = "0.0%"
    defect_count: int = 0
    inference_time_ms: float = 0.0
    recommendation: Optional[str] = ""
    standard_code: Optional[str] = "ACI"
    crack_depth_status: Optional[str] = "unknown"
    polygons: List[List[List[float]]] = Field(default_factory=list)
    normalized_polygons: List[List[List[float]]] = Field(default_factory=list)
    bounding_boxes: List[List[float]] = Field(default_factory=list)
    calibration: Optional[Dict[str, Any]] = Field(default_factory=dict)
    caliper_samples: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    multi_factor_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    assessment_breakdown: Optional[Dict[str, Any]] = Field(default_factory=dict)
    compliance_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    evidence_sufficiency: Optional[Dict[str, Any]] = Field(default_factory=dict)
    plain_language_explanation: Optional[str] = ""

class BatchAnalysisSummary(BaseModel):
    total_images: int
    cracks_detected: int
    no_cracks_detected: int
    highest_severity: str
    mean_confidence: float
    total_defects: int
    processed_at: datetime = Field(default_factory=datetime.utcnow)

class BatchAnalysisResponse(BaseModel):
    summary: BatchAnalysisSummary
    results: List[AnalysisResponse]

