import pytest
from app.services.morphometry import MorphometryService

def test_roadway_asphalt_fatigue_remediation():
    """Verify that flexible asphalt road surfaces with fatigue/alligator cracking
    prescribe AASHTO PP 44 / ISSA A143 cold-milling & HMA patching with traffic control,
    and strictly prohibit rigid epoxy."""
    spec = MorphometryService.generate_remediation_specification(
        structural_material="asphalt_bitumen",
        member_type="road_pavement",
        building_type="highway",
        crack_pattern="alligator_fatigue",
        severity="high",
        estimated_aperture_mm=5.5
    )

    assert "AASHTO PP 44" in spec["protocol_title"]
    assert "AASHTO PP 44" in spec["governing_standard"]
    assert "Asphalt Concrete" in spec["structural_material"]
    assert "Rigid epoxy injection is STRICTLY PROHIBITED" in spec["material_specification"]
    assert any("Cold Milling" in act for act in spec["prescribed_actions"])
    assert any("MUTCD" in act for act in spec["prescribed_actions"])
    assert any("milling planer" in eq.lower() for eq in spec["equipment_required"])
    assert "ACTIVE ROADWAY SAFETY HAZARD" in spec["safety_protocol"]

def test_roadway_asphalt_standard_crack_seal_remediation():
    """Verify standard asphalt crack prescribes ASTM D6690 / AASHTO M 324 hot-poured sealant."""
    spec = MorphometryService.generate_remediation_specification(
        structural_material="asphalt_concrete",
        member_type="road",
        crack_pattern="transverse",
        severity="medium",
        estimated_aperture_mm=3.2
    )

    assert "ASTM D6690" in spec["protocol_title"]
    assert "AASHTO M 324" in spec["governing_standard"]
    assert "Rigid structural epoxy is STRICTLY PROHIBITED" in spec["material_specification"]
    assert any("Reservoir Routing" in act for act in spec["prescribed_actions"])
    assert any("Heat Lance" in act for act in spec["prescribed_actions"])
    assert any("hot rubberized asphalt" in act.lower() for act in spec["prescribed_actions"])

def test_masonry_brickwork_remediation():
    """Verify brickwork prescribes TMS 402/602 helical stainless steel tie stitching and breathable lime mortar, prohibiting rigid epoxy."""
    spec = MorphometryService.generate_remediation_specification(
        structural_material="masonry_brick",
        member_type="masonry_pier",
        structural_system="bearing_masonry",
        crack_pattern="diagonal_stair_step",
        severity="medium",
        estimated_aperture_mm=2.5
    )

    assert "TMS 402/602" in spec["protocol_title"]
    assert "ASTM C270" in spec["governing_standard"]
    assert "Structural Brickwork" in spec["structural_material"]
    assert "High-modulus rigid epoxy is PROHIBITED" in spec["material_specification"]
    assert any("Helical Stitching" in act for act in spec["prescribed_actions"])
    assert any("Breathable Repointing" in act for act in spec["prescribed_actions"])
    assert any("hepa vacuum" in eq.lower() for eq in spec["equipment_required"])

def test_post_tensioned_safeguard_remediation():
    """Verify post-tensioned elements mandate GPR tendon scanning, 150mm zero-drilling zone, and PTI DC80.1 protocol."""
    spec = MorphometryService.generate_remediation_specification(
        structural_material="post_tensioned_concrete",
        member_type="pt_transfer_girder",
        structural_system="post_tensioned",
        crack_pattern="flexural_shear",
        severity="high",
        estimated_aperture_mm=0.45
    )

    assert "PTI DC80.1" in spec["protocol_title"]
    assert "ACI 423.7" in spec["governing_standard"]
    assert any("Tendon Mapping" in act for act in spec["prescribed_actions"])
    assert any("Zero-Drilling Zone" in act for act in spec["prescribed_actions"])
    assert "EXPLOSIVE STRAND FAILURE HAZARD" in spec["safety_protocol"]

def test_water_bearing_wet_concrete_remediation():
    """Verify wet element / basement retaining wall prescribes expanding polyurethane chemical grout conforming to EN 1504-5 / ACI 504R."""
    spec = MorphometryService.generate_remediation_specification(
        structural_material="reinforced_concrete",
        member_type="basement_retaining_wall",
        environmental_exposure="groundwater_hydrostatic",
        previous_water_leakage=True,
        crack_pattern="vertical_wall",
        severity="high",
        estimated_aperture_mm=0.8
    )

    assert "EN 1504-5" in spec["protocol_title"]
    assert "Polyurethane Chemical Grout" in spec["protocol_title"]
    assert any("Staggered Packer Drilling" in act for act in spec["prescribed_actions"])
    assert any("Water-Reactive Chemical Injection" in act for act in spec["prescribed_actions"])
    assert any("packer" in eq.lower() for eq in spec["equipment_required"])

def test_dry_reinforced_concrete_structural_remediation():
    """Verify standard dry RC beam / column near support prescribes ASTM C881 Type IV Grade 1 epoxy injection and structural shoring."""
    spec = MorphometryService.generate_remediation_specification(
        structural_material="reinforced_concrete",
        member_type="beam",
        crack_pattern="diagonal_shear",
        severity="high",
        estimated_aperture_mm=0.6,
        near_support=True,
        is_primary=True,
        visible_spalling=True
    )

    assert "ASTM C881" in spec["protocol_title"]
    assert "Reinforced Concrete" in spec["structural_material"]
    assert any("shoring" in act.lower() for act in spec["prescribed_actions"])
    assert any("Pressure Injection" in act for act in spec["prescribed_actions"])
    assert any("Corrosion Remediation" in act for act in spec["prescribed_actions"])
