import pytest
from app.services.yolo_service import YOLOv8SegmentationService

def test_yolo_service_initialization():
    service = YOLOv8SegmentationService()
    assert service.device in ["mps", "cuda", "cpu"]
    assert service.weights_path is not None

def test_yolo_service_clean_image_safety(blank_image_bytes):
    service = YOLOv8SegmentationService()
    result = service.segment(blank_image_bytes)
    assert "has_crack" in result
    assert "defect_count" in result
    assert "polygons" in result
    assert "normalized_polygons" in result
    assert "bounding_boxes" in result
    assert isinstance(result["polygons"], list)
    assert isinstance(result["normalized_polygons"], list)
    assert isinstance(result["bounding_boxes"], list)

def test_yolo_service_synthetic_crack_inference(synthetic_crack_image_bytes):
    service = YOLOv8SegmentationService()
    result = service.segment(synthetic_crack_image_bytes)
    assert result["dimensions"]["width"] == 640
    assert result["dimensions"]["height"] == 640
    # Coordinates must be bounded between 0 and 1 for normalized coordinates
    for poly in result["normalized_polygons"]:
        for pt in poly:
            assert 0.0 <= pt[0] <= 1.0
            assert 0.0 <= pt[1] <= 1.0
