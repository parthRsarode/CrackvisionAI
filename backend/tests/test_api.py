import io
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "engine" in data

@pytest.mark.asyncio
async def test_analyze_unsupported_file_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("test.txt", b"plain text content", "text/plain")}
        response = await client.post("/analyze", files=files)
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

@pytest.mark.asyncio
async def test_analyze_blank_image(blank_image_bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("blank.jpg", blank_image_bytes, "image/jpeg")}
        response = await client.post("/analyze", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "analysis_id" in data
        assert data["status"] in ["no_significant_crack", "crack_detected"]
        assert "has_segmentation" in data
        assert isinstance(data["polygons"], list)
        assert isinstance(data["normalized_polygons"], list)
        assert isinstance(data["bounding_boxes"], list)
        assert "inference_time_ms" in data

@pytest.mark.asyncio
async def test_analyze_synthetic_crack_image(synthetic_crack_image_bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("crack_test.jpg", synthetic_crack_image_bytes, "image/jpeg")}
        response = await client.post("/analyze", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_id"].startswith("ana_")
        assert "severity" in data
        assert "confidence" in data
        assert "recommendation" in data
        assert "aci_compliance" in data
        assert "calibration" in data
        assert "mm_per_pixel" in data["calibration"]

@pytest.mark.asyncio
async def test_calibrate_two_point_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "point1": [100.0, 100.0],
            "point2": [300.0, 100.0],
            "reference_length_mm": 50.0,
            "image_width": 1000
        }
        response = await client.post("/calibrate/two-point", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["calibration_status"] == "user_two_point_calibrated"
        assert data["pixel_distance"] == 200.0
        assert data["mm_per_pixel"] == 0.25
        assert data["reference_length_mm"] == 50.0

@pytest.mark.asyncio
async def test_probe_aperture_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "polygon": [
                [100.0, 50.0],
                [110.0, 50.0],
                [110.0, 250.0],
                [100.0, 250.0]
            ],
            "click_point": [105.0, 150.0],
            "mm_per_pixel": 0.2
        }
        response = await client.post("/calibrate/probe-aperture", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "width_px" in data
        assert "width_mm" in data
        assert "span_points" in data
        assert len(data["span_points"]) == 2

