import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean
)
from sqlalchemy.orm import relationship
from .session import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_tag = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    component_type = Column(String(128), default="Concrete Structural Element")
    location = Column(String(255), default="Field Site")
    building_type = Column(String(64), default="residential")
    construction_year = Column(Integer, nullable=True)
    structural_system = Column(String(128), default="unknown")
    structural_material = Column(String(128), default="reinforced_concrete")
    created_at = Column(DateTime, default=datetime.utcnow)

    surveys = relationship("Survey", back_populates="asset", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset_tag": self.asset_tag,
            "name": self.name,
            "component_type": self.component_type,
            "location": self.location,
            "building_type": self.building_type,
            "construction_year": self.construction_year,
            "structural_system": self.structural_system,
            "structural_material": self.structural_material,
            "survey_count": len(self.surveys) if self.surveys else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(String(128), unique=True, index=True, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), default="inspection.jpg")
    thumbnail_data = Column(Text, nullable=True)  # base64 or data uri
    
    # Analysis Verdict
    status = Column(String(64), default="no_significant_crack")
    severity = Column(String(32), default="low")
    confidence = Column(Float, default=0.0)
    crack_type = Column(String(128), default="None")
    estimated_width = Column(String(64), default="0.0 mm")
    max_aperture_mm = Column(Float, default=0.0)
    affected_area = Column(String(32), default="0.0%")
    defect_count = Column(Integer, default=0)
    inference_time_ms = Column(Float, default=0.0)
    recommendation = Column(Text, default="")
    standard_code = Column(String(32), default="ACI")
    crack_depth_status = Column(String(64), default="unknown")

    # Serialized Technical Payloads
    polygons_json = Column(Text, default="[]")
    normalized_polygons_json = Column(Text, default="[]")
    bounding_boxes_json = Column(Text, default="[]")
    calibration_json = Column(Text, default="{}")
    caliper_samples_json = Column(Text, default="[]")
    multi_factor_metrics_json = Column(Text, default="{}")
    assessment_breakdown_json = Column(Text, default="{}")
    compliance_details_json = Column(Text, default="{}")
    evidence_sufficiency_json = Column(Text, default="{}")
    plain_language_explanation = Column(Text, default="")
    building_profile_json = Column(Text, default="{}")
    age_deterioration_context_json = Column(Text, default="{}")

    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="surveys")
    defects = relationship("DefectFissure", back_populates="survey", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "survey_id": self.survey_id,
            "analysis_id": self.survey_id,
            "asset_id": self.asset_id,
            "asset_name": self.asset.name if self.asset else "Unassigned Field Site",
            "filename": self.filename,
            "thumbnail": self.thumbnail_data or "",
            "status": self.status,
            "severity": self.severity,
            "confidence": self.confidence,
            "crack_type": self.crack_type,
            "estimated_width": self.estimated_width,
            "max_aperture_mm": self.max_aperture_mm,
            "affected_area": self.affected_area,
            "defect_count": self.defect_count,
            "inference_time_ms": self.inference_time_ms,
            "recommendation": self.recommendation,
            "standard_code": self.standard_code,
            "crack_depth_status": self.crack_depth_status,
            "polygons": json.loads(self.polygons_json or "[]"),
            "normalized_polygons": json.loads(self.normalized_polygons_json or "[]"),
            "bounding_boxes": json.loads(self.bounding_boxes_json or "[]"),
            "calibration": json.loads(self.calibration_json or "{}"),
            "caliper_samples": json.loads(self.caliper_samples_json or "[]"),
            "multi_factor_metrics": json.loads(self.multi_factor_metrics_json or "{}"),
            "assessment_breakdown": json.loads(self.assessment_breakdown_json or "{}"),
            "compliance_details": json.loads(self.compliance_details_json or "{}"),
            "evidence_sufficiency": json.loads(self.evidence_sufficiency_json or "{}"),
            "plain_language_explanation": self.plain_language_explanation,
            "building_profile": json.loads(self.building_profile_json or "{}"),
            "age_deterioration_context": json.loads(self.age_deterioration_context_json or "{}"),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class DefectFissure(Base):
    __tablename__ = "defect_fissures"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    polygon_json = Column(Text, default="[]")
    bounding_box_json = Column(Text, default="[]")
    confidence = Column(Float, default=0.0)
    aperture_mm = Column(Float, default=0.0)

    survey = relationship("Survey", back_populates="defects")
