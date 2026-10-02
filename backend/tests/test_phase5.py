import io
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_assets_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Asset
        payload = {
            "asset_tag": "PIER-EAST-09",
            "name": "East Bridge Pier Column",
            "component_type": "Reinforced Column",
            "location": "Sector 4 North"
        }
        resp = await client.post("/api/assets", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset_tag"] == "PIER-EAST-09"
        assert data["name"] == "East Bridge Pier Column"

        # 2. List Assets
        list_resp = await client.get("/api/assets")
        assert list_resp.status_code == 200
        assets = list_resp.json()
        assert any(a["asset_tag"] == "PIER-EAST-09" for a in assets)

@pytest.mark.asyncio
async def test_surveys_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Save Survey
        survey_payload = {
            "survey_id": "SURV-TEST-88",
            "status": "crack_detected",
            "severity": "high",
            "confidence": 94.2,
            "crack_type": "Diagonal shear crack",
            "estimated_width": "0.55 mm",
            "affected_area": "4.1%",
            "standard_code": "ACI",
            "defect_count": 2,
            "caliper_samples": [
                {"id": "CAL-01", "width_mm": 0.55, "width_px": 2.2, "timestamp": "12:00:00"}
            ]
        }
        save_resp = await client.post("/api/surveys", json=survey_payload)
        assert save_resp.status_code == 200
        saved = save_resp.json()
        assert saved["survey_id"] == "SURV-TEST-88"

        # 2. List Surveys with severity filter
        list_resp = await client.get("/api/surveys?severity=high")
        assert list_resp.status_code == 200
        surveys = list_resp.json()
        assert any(s["survey_id"] == "SURV-TEST-88" for s in surveys)

        # 3. Get Survey by ID
        get_resp = await client.get("/api/surveys/SURV-TEST-88")
        assert get_resp.status_code == 200
        assert get_resp.json()["survey_id"] == "SURV-TEST-88"
        assert len(get_resp.json()["caliper_samples"]) == 1

        # 4. Delete Survey
        del_resp = await client.delete("/api/surveys/SURV-TEST-88")
        assert del_resp.status_code == 200
        assert del_resp.json()["status"] == "deleted"

        # 5. Confirm 404 after deletion
        get_after = await client.get("/api/surveys/SURV-TEST-88")
        assert get_after.status_code == 404

@pytest.mark.asyncio
async def test_survey_pdf_download():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Save a survey first
        survey_payload = {
            "survey_id": "SURV-PDF-01",
            "status": "crack_detected",
            "severity": "medium",
            "confidence": 88.5,
            "crack_type": "Vertical shrinkage crack",
            "estimated_width": "0.28 mm",
            "standard_code": "ACI"
        }
        await client.post("/api/surveys", json=survey_payload)

        # Download PDF
        pdf_resp = await client.get("/api/surveys/SURV-PDF-01/pdf")
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        assert pdf_resp.content.startswith(b"%PDF")
        assert len(pdf_resp.content) > 1000

        # Clean up
        await client.delete("/api/surveys/SURV-PDF-01")

@pytest.mark.asyncio
async def test_survey_pdf_export_direct():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        direct_payload = {
            "survey_id": "DIRECT-SCAR-99",
            "status": "crack_detected",
            "severity": "high",
            "confidence": 97.0,
            "crack_type": "Diagonal shear crack",
            "estimated_width": "0.62 mm",
            "standard_code": "EC2",
            "caliper_samples": [
                {"id": "CAL-01", "width_mm": 0.62, "width_px": 2.8, "timestamp": "12:30:00"}
            ]
        }
        pdf_resp = await client.post("/api/surveys/export-pdf", json=direct_payload)
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        assert pdf_resp.content.startswith(b"%PDF")

@pytest.mark.asyncio
async def test_batch_analysis_endpoint(blank_image_bytes, synthetic_crack_image_bytes):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = [
            ("files", ("img1.jpg", blank_image_bytes, "image/jpeg")),
            ("files", ("img2.jpg", synthetic_crack_image_bytes, "image/jpeg"))
        ]
        resp = await client.post("/analyze/batch", files=files, data={"standard_code": "ACI"})
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "results" in data
        assert data["summary"]["total_images"] == 2
        assert len(data["results"]) == 2
