import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .models import Asset, Survey, DefectFissure

class SurveyRepository:

    @staticmethod
    def get_or_create_default_asset(db: Session, asset_tag: str = "FIELD-01", name: str = "General Survey Site") -> Asset:
        asset = db.query(Asset).filter(Asset.asset_tag == asset_tag).first()
        if not asset:
            asset = Asset(
                asset_tag=asset_tag,
                name=name,
                component_type="Structural Concrete",
                location="Field Survey"
            )
            db.add(asset)
            db.commit()
            db.refresh(asset)
        return asset

    @staticmethod
    def list_assets(db: Session) -> List[Dict[str, Any]]:
        assets = db.query(Asset).order_by(Asset.name).all()
        return [a.to_dict() for a in assets]

    @staticmethod
    def create_asset(
        db: Session,
        asset_tag: str,
        name: str,
        component_type: str = "Structural Element",
        location: str = "Field Site",
        building_type: str = "residential",
        construction_year: Optional[int] = None,
        structural_system: str = "unknown",
        structural_material: str = "reinforced_concrete"
    ) -> Dict[str, Any]:
        existing = db.query(Asset).filter(Asset.asset_tag == asset_tag).first()
        if existing:
            return existing.to_dict()
        asset = Asset(
            asset_tag=asset_tag,
            name=name,
            component_type=component_type,
            location=location,
            building_type=building_type,
            construction_year=construction_year,
            structural_system=structural_system,
            structural_material=structural_material
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset.to_dict()

    @staticmethod
    def save_survey(db: Session, data: Dict[str, Any], thumbnail_data: Optional[str] = None) -> Dict[str, Any]:
        survey_id = data.get("survey_id") or data.get("analysis_id")
        if not survey_id:
            raise ValueError("survey_id or analysis_id required")

        # Check if already exists; if so, update
        existing = db.query(Survey).filter(Survey.survey_id == survey_id).first()
        
        asset_id = data.get("asset_id")
        if not asset_id:
            default_asset = SurveyRepository.get_or_create_default_asset(db)
            asset_id = default_asset.id

        if not existing:
            survey = Survey(survey_id=survey_id)
            db.add(survey)
        else:
            survey = existing

        survey.asset_id = asset_id
        survey.filename = data.get("filename", survey.filename or "inspection.jpg")
        if thumbnail_data:
            survey.thumbnail_data = thumbnail_data
        elif data.get("thumbnail"):
            survey.thumbnail_data = data["thumbnail"]

        survey.status = data.get("status", "no_significant_crack")
        survey.severity = data.get("severity", "low")
        survey.confidence = float(data.get("confidence", 0.0))
        survey.crack_type = data.get("crack_type", "None")
        survey.estimated_width = data.get("estimated_width", "0.0 mm")
        survey.affected_area = str(data.get("affected_area", "0.0%"))
        survey.defect_count = int(data.get("defect_count", 0))
        survey.inference_time_ms = float(data.get("inference_time_ms", 0.0))
        survey.recommendation = str(data.get("recommendation", ""))
        survey.standard_code = str(data.get("standard_code") or "ACI")
        survey.crack_depth_status = str(data.get("crack_depth_status", "unknown"))

        # Max aperture extraction
        if "max_aperture_mm" in data:
            survey.max_aperture_mm = float(data["max_aperture_mm"])
        else:
            try:
                parts = survey.estimated_width.replace("mm", "").split("-")
                survey.max_aperture_mm = float(parts[-1].strip())
            except Exception:
                survey.max_aperture_mm = 0.0

        # Technical JSON payloads
        survey.polygons_json = json.dumps(data.get("polygons") or [])
        survey.normalized_polygons_json = json.dumps(data.get("normalized_polygons") or [])
        survey.bounding_boxes_json = json.dumps(data.get("bounding_boxes") or [])
        survey.calibration_json = json.dumps(data.get("calibration") or {})
        survey.caliper_samples_json = json.dumps(data.get("caliper_samples") or [])
        survey.multi_factor_metrics_json = json.dumps(data.get("multi_factor_metrics") or {})
        survey.assessment_breakdown_json = json.dumps(data.get("assessment_breakdown") or {})
        survey.compliance_details_json = json.dumps(data.get("compliance_details") or {})
        survey.evidence_sufficiency_json = json.dumps(data.get("evidence_sufficiency") or {})
        survey.plain_language_explanation = str(data.get("plain_language_explanation", ""))
        survey.building_profile_json = json.dumps(data.get("building_profile") or {})
        survey.age_deterioration_context_json = json.dumps(data.get("age_deterioration_context") or {})

        db.commit()
        db.refresh(survey)
        return survey.to_dict()

    @staticmethod
    def list_surveys(
        db: Session,
        severity: Optional[str] = None,
        standard_code: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        query = db.query(Survey)
        if severity and severity != "all":
            query = query.filter(Survey.severity == severity.lower())
        if standard_code and standard_code != "all":
            query = query.filter(Survey.standard_code == standard_code.upper())

        surveys = query.order_by(Survey.created_at.desc()).offset(offset).limit(limit).all()
        return [s.to_dict() for s in surveys]

    @staticmethod
    def get_survey(db: Session, survey_id: str) -> Optional[Dict[str, Any]]:
        survey = db.query(Survey).filter(Survey.survey_id == survey_id).first()
        if not survey:
            return None
        return survey.to_dict()

    get_survey_by_id = get_survey

    @staticmethod
    def delete_survey(db: Session, survey_id: str) -> bool:
        survey = db.query(Survey).filter(Survey.survey_id == survey_id).first()
        if not survey:
            return False
        db.delete(survey)
        db.commit()
        return True
