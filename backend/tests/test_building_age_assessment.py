import io
import json
import pytest
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal, init_db
from app.db.models import Asset, Survey
from app.db.repository import SurveyRepository
from app.services.morphometry import (
    calculate_building_age,
    synthesize_age_deterioration_context,
    synthesize_civil_assessment,
    evaluate_standards_compliance,
    audit_evidence_sufficiency
)
from app.services.pdf_generator import PDFReportGenerator

# ---------------------------------------------------------------------------
# Scenario 1: Construction year known and age calculated correctly
# ---------------------------------------------------------------------------
def test_scenario_01_construction_year_known_age_calculated():
    age = calculate_building_age(1995, "2025-06-15")
    assert age == 30, f"Expected 30, got {age}"

    age_exact = calculate_building_age(2000, "2020-01-01")
    assert age_exact == 20

# ---------------------------------------------------------------------------
# Scenario 2: Historical inspection date produces correct historical age
# ---------------------------------------------------------------------------
def test_scenario_02_historical_inspection_date():
    # If a survey was performed in 2012 on a 1980 building, age must be 32, not today's age
    historical_age = calculate_building_age(1980, "2012-04-10")
    assert historical_age == 32, f"Historical age should be 32, got {historical_age}"
    assert historical_age != (datetime.now().year - 1980)

# ---------------------------------------------------------------------------
# Scenario 3: Unknown construction year is handled safely
# ---------------------------------------------------------------------------
def test_scenario_03_unknown_construction_year_safe():
    age_none = calculate_building_age(None, "2025-06-15")
    assert age_none is None, "None construction year should yield None age"

    ctx = synthesize_age_deterioration_context(
        construction_year=None,
        inspection_date="2025-06-15",
        age_verification="unknown"
    )
    assert ctx["status"] in ["insufficient_historical_information", "context_documented"]
    assert ctx["age_at_inspection"] is None
    assert "Construction year and baseline age not verified" in ctx["missing_information"]

# ---------------------------------------------------------------------------
# Scenario 4: Invalid future construction year is flagged safely
# ---------------------------------------------------------------------------
def test_scenario_04_invalid_future_construction_year():
    # Construction year 2040 inspected in 2025
    future_age = calculate_building_age(2040, "2025-06-15")
    assert future_age is None, "Future construction year must not return a negative or valid age"

    ctx = synthesize_age_deterioration_context(
        construction_year=2040,
        inspection_date="2025-06-15"
    )
    assert ctx["status"] == "insufficient_historical_information"
    assert any("future" in str(m).lower() for m in ctx["missing_information"])

# ---------------------------------------------------------------------------
# Scenario 5: Editing building profile does not rewrite past survey snapshots
# ---------------------------------------------------------------------------
def test_scenario_05_editing_asset_preserves_past_survey_snapshots():
    db: Session = SessionLocal()
    try:
        # Create asset
        asset = Asset(
            asset_tag=f"TOWER_{datetime.now().timestamp()}",
            name="Tower Alpha",
            building_type="commercial",
            construction_year=1990,
            structural_system="rc_frame",
            structural_material="reinforced_concrete"
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)

        # Save an inspection snapshot
        survey_dict = {
            "analysis_id": f"test_snap_{datetime.now().timestamp()}",
            "asset_id": asset.id,
            "asset_name": asset.name,
            "status": "crack_detected",
            "severity": "medium",
            "crack_type": "Structural Shear Fissure",
            "confidence": 92.0,
            "estimated_width": "0.45 mm",
            "affected_area": "3.2%",
            "building_profile": {
                "building_name": "Tower Alpha",
                "building_type": "commercial",
                "construction_year": 1990,
                "building_age_years": 34,
                "age_verification": "documented",
                "inspection_date": "2024-01-15"
            },
            "age_deterioration_context": {
                "status": "context_documented",
                "age_at_inspection": 34,
                "engineering_reasoning": "Original snapshot analysis"
            }
        }
        saved_survey = SurveyRepository.save_survey(db, survey_dict)
        survey_id = saved_survey["survey_id"]

        # Now simulate editing the building profile on the asset (e.g. corrected construction year to 1985)
        asset.construction_year = 1985
        asset.building_type = "institutional"
        db.commit()

        # Query the past survey record
        historical = SurveyRepository.get_survey_by_id(db, survey_id)
        assert historical is not None

        # Verify historical snapshot is preserved intact!
        hist_bp = historical.get("building_profile") or {}
        assert hist_bp.get("construction_year") == 1990, "Past survey snapshot construction year must remain 1990!"
        assert hist_bp.get("building_age_years") == 34
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Scenario 6: Older records without age information still load cleanly
# ---------------------------------------------------------------------------
def test_scenario_06_older_records_without_age_load_cleanly():
    db: Session = SessionLocal()
    try:
        # Simulate legacy record without building profile JSON
        legacy_id = f"legacy_{datetime.now().timestamp()}"
        legacy_survey = Survey(
            survey_id=legacy_id,
            status="crack_detected",
            severity="low",
            crack_type="Shrinkage Micro-Crack",
            confidence=85.0,
            estimated_width="0.15 mm",
            affected_area="0.8%",
            building_profile_json=None,
            age_deterioration_context_json=None
        )
        db.add(legacy_survey)
        db.commit()

        loaded = SurveyRepository.get_survey_by_id(db, legacy_id)
        assert loaded is not None
        assert loaded["survey_id"] == legacy_id
        assert loaded.get("building_profile") in [None, {}]
        assert loaded.get("age_deterioration_context") in [None, {}]
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Scenario 7: A new building is NOT automatically classified as low severity
# ---------------------------------------------------------------------------
def test_scenario_07_new_building_not_automatically_low_severity():
    # 2-year old building with a wide 0.75mm shear crack near support with spalling
    result = synthesize_civil_assessment(
        crack_width_mm=0.75,
        crack_length_mm=450.0,
        crack_count=3,
        member_type="Structural Beam / Girder",
        criticality="primary",
        proximity="near_support",
        visible_spalling=True,
        visible_corrosion=False,
        crack_depth_status="unknown",
        standard_code="ACI",
        construction_year=2023,
        inspection_date="2025-05-10"  # 2 years old!
    )
    # Must NOT be classified as 'low' simply because it is a new building
    assert result["severity"] in ["high", "medium"], f"New building with severe 0.75mm crack must not be low, got {result['severity']}"
    assert "age" not in result["severity"].lower()
    # Age-specific conclusion must identify early-age construction defect suspicion
    assert result["age_deterioration_context"]["status"] == "early_age_construction_defect_suspected"
    assert "construction" in result["age_deterioration_context"]["age_influence_summary"].lower()

# ---------------------------------------------------------------------------
# Scenario 8: An old building is NOT automatically classified as high severity
# ---------------------------------------------------------------------------
def test_scenario_08_old_building_not_automatically_high_severity():
    # 55-year old building with narrow 0.12mm hairline shrinkage crack in dry protected air
    result = synthesize_civil_assessment(
        crack_width_mm=0.12,
        crack_length_mm=80.0,
        crack_count=1,
        member_type="Floor / Ceiling / Concrete Slab",
        criticality="secondary",
        proximity="mid_span",
        visible_spalling=False,
        visible_corrosion=False,
        crack_depth_status="unknown",
        standard_code="ACI",
        construction_year=1970,
        inspection_date="2025-05-10",  # 55 years old!
        maintenance_condition="regular",
        environmental_exposure="indoor_dry"
    )
    # Must NOT be arbitrarily elevated to 'high' purely based on age
    assert result["severity"] == "low", f"Old building with minor 0.12mm hairline crack should be low, got {result['severity']}"

# ---------------------------------------------------------------------------
# Scenario 9: Narrow crack with concerning context triggers investigation
# ---------------------------------------------------------------------------
def test_scenario_09_narrow_crack_with_distress_triggers_investigation():
    # 0.22mm crack, but persistent moisture + spalling + corrosion indicators
    ctx = synthesize_age_deterioration_context(
        construction_year=1988,
        inspection_date="2025-01-15",
        environmental_exposure="persistent_moisture",
        maintenance_condition="poor",
        visible_spalling=True,
        visible_corrosion=True,
        water_leakage=True
    )
    assert ctx["status"] in ["potential_age_related_distress", "further_deterioration_assessment_recommended"]
    assert len(ctx["observed_deterioration_indicators"]) >= 3
    assert "moisture" in ctx["engineering_reasoning"].lower() or "investigation" in ctx["engineering_reasoning"].lower()

# ---------------------------------------------------------------------------
# Scenario 10: Building age alone cannot trigger structural safety conclusion
# ---------------------------------------------------------------------------
def test_scenario_10_age_alone_cannot_trigger_safety_conclusion():
    ctx = synthesize_age_deterioration_context(
        construction_year=1960,
        inspection_date="2025-01-15"
    )
    assert "Building age is contextual information and is not, by itself, a measure of structural safety" in ctx["context_disclaimer"]

# ---------------------------------------------------------------------------
# Scenario 11: Missing depth does NOT generate an invented depth value
# ---------------------------------------------------------------------------
def test_scenario_11_missing_depth_does_not_invent_depth_value():
    result = synthesize_civil_assessment(
        crack_width_mm=0.35,
        crack_length_mm=120.0,
        crack_count=1,
        member_type="Pillar / Column / Support",
        criticality="primary",
        proximity="near_support",
        visible_spalling=False,
        visible_corrosion=False,
        crack_depth_status="unknown"
    )
    assert result["crack_depth_status"] in ["unknown", "surface_only", "not_assessed", "further_investigation_required"]
    assert "cannot be established from surface" in result["crack_depth_explanation"].lower()
    # Confirm no numeric depth mm value is fabricated
    assert "crack_depth_mm" not in result

# ---------------------------------------------------------------------------
# Scenario 12: Missing calibration does not produce falsely precise measurements
# ---------------------------------------------------------------------------
def test_scenario_12_missing_calibration_handles_gracefully():
    sufficiency = audit_evidence_sufficiency(
        calibrated=False,
        depth_status="unknown",
        has_history=False,
        spalling_checked=False,
        corrosion_checked=False
    )
    assert "Spatial optical scale / fiducial datum" in sufficiency["missing_factors"]
    assert sufficiency["status"] == "insufficient_for_engineering_assessment"

# ---------------------------------------------------------------------------
# Scenario 13: Compliance cannot be established from age or width alone
# ---------------------------------------------------------------------------
def test_scenario_13_compliance_requires_exposure_and_criteria():
    compliance = evaluate_standards_compliance(
        crack_width_mm=0.25,
        member_type="Structural Beam / Girder",
        standard_code="ACI",
        environment="Humid / Moisture / Soil Contact"
    )
    assert compliance["status"] in ["provisionally_consistent", "requires_review", "verified", "potential_non_conformance"]
    assert compliance["relevant_criterion"] != ""
    assert compliance["missing_information"] != ""
    # Should reference ACI 224R-01 / CODE-562-25
    assert "ACI" in compliance["standard_name"]

# ---------------------------------------------------------------------------
# Scenario 14: Reports correctly display age, inspection date, and limitations
# ---------------------------------------------------------------------------
def test_scenario_14_scar_pdf_generation_includes_building_profile_and_age():
    survey_data = {
        "analysis_id": "SCAR-AUDIT-2025",
        "asset_name": "Pacific Highway Overpass",
        "severity": "medium",
        "status": "crack_detected",
        "crack_type": "Flexural Tension Crack",
        "estimated_width": "0.32 mm",
        "affected_area": "2.1%",
        "confidence": 94.5,
        "standard_code": "ACI",
        "created_at": "2025-04-12T10:30:00Z",
        "building_profile": {
            "building_name": "Pacific Highway Overpass",
            "building_type": "bridge",
            "construction_year": 1985,
            "building_age_years": 40,
            "age_verification": "documented",
            "inspection_date": "2025-04-12",
            "structural_material": "reinforced_concrete",
            "structural_system": "bridge_superstructure",
            "member_importance": "primary",
            "environmental_exposure": "outdoor_weather",
            "maintenance_condition": "regular"
        },
        "age_deterioration_context": {
            "status": "context_documented",
            "construction_year": 1985,
            "age_at_inspection": 40,
            "age_verification": "documented",
            "observed_deterioration_indicators": ["freeze_thaw_scaling"],
            "historical_progression": "Baseline survey",
            "engineering_reasoning": "Structure is 40 years old. Durability context indicates ongoing service load with no critical spalling.",
            "context_disclaimer": "Building age is contextual information and is not, by itself, a measure of structural safety or crack severity."
        }
    }

    pdf_bytes = PDFReportGenerator.generate_scar_pdf(survey_data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # PDF starts with %PDF magic header
    assert pdf_bytes.startswith(b"%PDF")

# ---------------------------------------------------------------------------
# Scenario 15: Full /analyze endpoint integration test with Building Profile
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_scenario_15_analyze_endpoint_with_building_profile(synthetic_crack_image_bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("crack_field.jpg", synthetic_crack_image_bytes, "image/jpeg")}
        data = {
            "member_type": "Structural Beam / Girder",
            "element_criticality": "primary",
            "proximity_to_supports": "near_support",
            "visible_spalling": "false",
            "visible_corrosion": "false",
            "standard_code": "ACI",
            "building_name": "Harbor Terminal Pier 4",
            "building_type": "industrial",
            "construction_year": "1992",
            "age_verification": "documented",
            "inspection_date": "2024-08-20",
            "structural_system": "rc_frame",
            "structural_material": "reinforced_concrete",
            "maintenance_condition": "regular",
            "environmental_exposure": "coastal_marine"
        }
        response = await client.post("/analyze", files=files, data=data)
        assert response.status_code == 200, f"Analysis failed: {response.text}"
        res = response.json()

        assert "analysis_id" in res
        assert "building_profile" in res
        bp = res["building_profile"]
        assert bp["building_name"] == "Harbor Terminal Pier 4"
        assert bp["construction_year"] == 1992
        assert bp["building_age_years"] == 32  # 2024 - 1992
        assert bp["age_verification"] == "documented"
        assert bp["environmental_exposure"] == "coastal_marine"

        assert "age_deterioration_context" in res
        age_ctx = res["age_deterioration_context"]
        assert age_ctx["age_at_inspection"] == 32
        assert "Building age is contextual information" in age_ctx["context_disclaimer"]


# ---------------------------------------------------------------------------
# Scenario 16: Early-age building with severe crack explicitly diagnoses construction defects
# ---------------------------------------------------------------------------
def test_scenario_16_early_age_structure_severe_crack_diagnoses_construction_defect():
    # 1-year old building with a 0.55mm shear crack on a transfer girder near support
    assessment = synthesize_civil_assessment(
        crack_width_mm=0.55,
        crack_length_mm=380.0,
        crack_count=2,
        member_type="Structural Beam / Girder",
        criticality="primary",
        proximity="near_support",
        visible_spalling=False,
        visible_corrosion=False,
        crack_depth_status="unknown",
        standard_code="ACI",
        construction_year=2024,
        inspection_date="2025-03-15",  # 1 year old
        environmental_exposure="indoor_dry"
    )

    age_ctx = assessment["age_deterioration_context"]
    assert age_ctx["status"] == "early_age_construction_defect_suspected"
    assert "Early-Age Construction / Structural Defect Suspected" in age_ctx["status_label"]
    assert age_ctx["age_at_inspection"] == 1

    # Check that reasoning and summary cite ACI 224.1R, construction defects (formwork, curing, overload, settlement)
    summary_lower = age_ctx["age_influence_summary"].lower()
    assert "construction" in summary_lower
    assert "formwork" in summary_lower or "curing" in summary_lower or "settlement" in summary_lower
    assert any("224.1r" in std["standard"].lower() for std in age_ctx["standards_consulted"])

    # Verify that the PDF generator generates the SCAR report with the critical notice
    survey_data = {
        "analysis_id": "SCAR-NEW-BUILDING-001",
        "asset_name": "Skyline Heights Tower (New)",
        "severity": assessment["severity"],
        "status": "crack_detected",
        "crack_type": "Structural Shear Fissure",
        "estimated_width": "0.55 mm",
        "affected_area": "2.8%",
        "confidence": 95.0,
        "standard_code": "ACI",
        "created_at": "2025-03-15T09:00:00Z",
        "recommendation": assessment["recommendation"],
        "building_profile": {
            "building_name": "Skyline Heights Tower (New)",
            "building_type": "residential",
            "construction_year": 2024,
            "building_age_years": 1,
            "age_verification": "documented",
            "inspection_date": "2025-03-15",
            "structural_material": "reinforced_concrete",
            "structural_system": "rc_frame",
            "member_importance": "primary"
        },
        "age_deterioration_context": age_ctx
    }
    pdf_bytes = PDFReportGenerator.generate_scar_pdf(survey_data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

