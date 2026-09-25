from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

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
