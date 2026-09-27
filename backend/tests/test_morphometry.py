import pytest
from app.services.morphometry import MorphometryService

def test_morphometry_tie_hole_filtering():
    service = MorphometryService()
    # Circular tie-hole: 80x80 box (aspect ratio 1.0, area 6400)
    circular_box = [280.0, 280.0, 360.0, 360.0]
    circular_poly = [[280.0, 320.0], [320.0, 360.0], [360.0, 320.0], [320.0, 280.0]]
    
    # Elongated crack: 20x300 box (aspect ratio 15.0, area 6000)
    crack_box = [100.0, 100.0, 120.0, 400.0]
    crack_poly = [[100.0, 100.0], [120.0, 100.0], [120.0, 400.0], [100.0, 400.0]]

    polys = [circular_poly, crack_poly]
    boxes = [circular_box, crack_box]
    confs = [85.0, 92.0]

    filtered_polys, filtered_boxes, filtered_confs = service.filter_artifacts(polys, boxes, confs)

    # Circular tie-hole should be filtered out, crack should remain
    assert len(filtered_polys) == 1
    assert filtered_boxes[0] == crack_box
    assert filtered_confs[0] == 92.0

def test_morphometry_orientation_classification():
    service = MorphometryService()
    # Vertical crack: dx=10, dy=200 -> angle ~87°
    vert_box = [100.0, 100.0, 110.0, 300.0]
    assert service.classify_orientation(vert_box) == "Vertical shrinkage crack"

    # Diagonal shear crack: dx=100, dy=100 -> angle 45°
    diag_box = [100.0, 100.0, 200.0, 200.0]
    assert service.classify_orientation(diag_box) == "Diagonal shear crack"

    # Horizontal settlement crack: dx=300, dy=20 -> angle ~3.8°
    horiz_box = [50.0, 100.0, 350.0, 120.0]
    assert service.classify_orientation(horiz_box) == "Horizontal settlement crack"

def test_morphometry_aperture_and_aci_compliance():
    service = MorphometryService()
    # Empty case
    empty_res = service.estimate_aperture_and_severity([], 640, 640)
    assert empty_res["severity"] == "low"
    assert empty_res["estimated_width"] == "0.0 mm"
    assert empty_res["aci_compliance"]["water_retaining"] is True

    # Real crack polygon
    poly = [[100.0, 100.0], [102.0, 100.0], [102.0, 400.0], [100.0, 400.0]]
    res = service.estimate_aperture_and_severity([poly], 640, 640, assumed_field_width_m=1.0)
    assert "severity" in res
    assert "estimated_width" in res
    assert "aci_compliance" in res
    assert "recommendation" in res
