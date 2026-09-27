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
