# External Integrations & API Contracts

## Backend Endpoints

The backend is an ASGI service built on FastAPI running on `http://localhost:8000`.

### 1. Health Verification
- **Path**: `GET /health`
- **Purpose**: System liveness check, polled periodically by frontend status badge.
- **Response**:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-09-25T12:00:00.000000"
  }
  ```

### 2. Crack Analysis Pipeline
- **Path**: `POST /analyze`
- **Content-Type**: `multipart/form-data`
- **Request Parameters**:
  - `file`: UploadFile (Allowed mime types: `image/jpeg`, `image/jpg`, `image/png`, `image/webp`). Limit: 5MB on backend API validation.
- **Response Model**: `AnalysisResponse` (Pydantic v2 schema)
  ```json
  {
    "analysis_id": "ana_4121_1790155942",
    "status": "crack_detected | no_significant_crack",
    "confidence": 87.8,
    "crack_type": "Vertical shrinkage crack",
    "severity": "low | medium | high",
    "estimated_width": "0.4 - 1.2 mm",
    "affected_area": "7.9%",
    "recommendation": "Schedule a detailed visual inspection and seal the surface crack...",
    "inspection_note": "This is an AI-assisted preliminary assessment...",
    "annotated_image_note": "Crack regions highlighted in red",
    "created_at": "2026-09-25T12:00:00.000000"
  }
  ```

## CORS Policy

- **Middleware**: `fastapi.middleware.cors.CORSMiddleware`
- **Origins**: `["*"]` (Permits cross-origin requests from `http://localhost:3001`, `http://localhost:3000`, `http://localhost:5173`)
- **Allowed Methods**: `["*"]` (GET, POST, OPTIONS, etc.)
- **Allowed Headers**: `["*"]`
- **Credentials**: `true`

## External Data & Persistence

- **Browser LocalStorage**:
  - Key: `crackvision-history`
  - Format: JSON array of `AnalysisHistoryItem` objects (limited to last 50 assessments).
  - Contains full analysis results plus client-generated thumbnail object URLs.
- **Export Formats**:
  - **CSV**: Client-side compiled comma-separated survey data (`civil_survey_log_YYYY-MM-DD.csv`).
  - **Print / PDF**: `@media print` CSS stylesheet formatting a standard ACI/ASTM Structural Condition Assessment Report (SCAR).

## Future Model Integration Interface

The backend `CrackAnalyzer` class in `backend/app/services/crack_analyzer.py` is architected as an adapter pattern:
- **Current State**: Deterministic mock seeded by file hash and byte length, producing realistic civil infrastructure crack measurements and classifications.
- **Target State (YOLOv8)**:
  ```python
  from ultralytics import YOLO
  self.model = YOLO('models/yolov8_crack_segmentation.pt')
  results = self.model(image)
  # Extract polygon masks, calculate pixel-to-metric width via calibration target
  ```
