from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

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
