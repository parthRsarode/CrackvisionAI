import pytest
import numpy as np
import cv2
from app.services.calibration_service import CalibrationService

def test_calibration_service_two_point():
    service = CalibrationService()
    # 200 pixels apart, known distance = 50.0 mm
    p1 = (100.0, 100.0)
    p2 = (300.0, 100.0)
    res = service.compute_two_point_scale(p1, p2, 50.0, 1000)
    
    assert res["calibration_status"] == "user_two_point_calibrated"
    assert res["pixel_distance"] == 200.0
    assert res["reference_length_mm"] == 50.0
    assert res["mm_per_pixel"] == 0.25  # 50mm / 200px = 0.25 mm/px
    assert res["assumed_field_width_m"] == 0.25  # (0.25 * 1000) / 1000 = 0.25m

def test_calibration_service_uncalibrated_fallback():
    service = CalibrationService()
    # Blank 640x640 grey image
    blank = np.full((640, 640), 128, dtype=np.uint8)
    res = service.detect_fiducial_marker(blank, marker_size_mm=50.0, default_field_width_m=0.15)
    
    assert res["calibration_status"] == "uncalibrated_macro"
    assert res["method"] == "default_macro"
    assert res["marker_id"] is None
    assert len(res["marker_corners"]) == 0
    assert res["mm_per_pixel"] > 0

def test_calibration_service_synthetic_aruco_detection():
    service = CalibrationService()
    
    # Generate a real ArUco 4x4 marker (id=3, size=200px)
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker = cv2.aruco.generateImageMarker(d, 3, 200)
    # Add 50px white margin around it (quiet zone)
    padded = cv2.copyMakeBorder(marker, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=255)
    
    # Test detection
    res = service.detect_fiducial_marker(padded, marker_size_mm=50.0)
    
    assert res["calibration_status"] == "fiducial_calibrated"
    assert res["method"] == "aruco_fiducial"
    assert res["marker_id"] == 3
    assert len(res["marker_corners"]) == 4
    # Marker is 200px across, 50mm -> ~0.25 mm/px
    assert 0.23 <= res["mm_per_pixel"] <= 0.27
    assert res["confidence"] > 90.0

def test_calibration_service_localized_aperture_sampling():
    service = CalibrationService()
    # Crack polygon: vertical strip from x=90 to 110, y=50 to 250 (width=20px)
    poly = [
        [90.0, 50.0],
        [110.0, 50.0],
        [110.0, 250.0],
        [90.0, 250.0]
    ]
    click_pt = (100.0, 150.0)
    mm_per_px = 0.2
    
    sample = service.sample_localized_aperture(poly, click_pt, mm_per_px)
    
    assert "width_px" in sample
    assert "width_mm" in sample
    assert "span_points" in sample
    assert len(sample["span_points"]) == 2
    # Width is ~20px -> ~4.0 mm
    assert 18.0 <= sample["width_px"] <= 22.0
    assert 3.6 <= sample["width_mm"] <= 4.4
