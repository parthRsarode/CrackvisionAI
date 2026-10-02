# Phase 05 Plan: Persistent Database, Formal PDF Generation & Batch Analysis

## Overview
Implement persistent SQLite storage via SQLAlchemy, RESTful CRUD endpoints for historical inspection management, formal ReportLab PDF generation for Structural Condition Assessment Reports (SCAR), and multi-image batch inspection processing.

## Requirements Covered
- **REQ-4.1**: SQLite database schema for assets, surveys, and defect records with SQLAlchemy ORM.
- **REQ-4.2**: RESTful CRUD endpoints for historical inspection and asset management (`/api/surveys`, `/api/assets`).
- **REQ-4.3**: Formal PDF export generation on the backend via ReportLab with annotated image, compliance matrix, caliper log, and PE sign-off block.
- **REQ-4.4**: Batch image inspection upload and concurrent processing for drone and terrestrial surveys (`POST /analyze/batch`).

## Implementation Plan

### 1. Database Architecture & ORM (`backend/app/db/`)
- `backend/app/db/session.py`: SQLite database engine, sessionmaker, and database initialization.
- `backend/app/db/models.py`:
  - `Asset`: ID, name, component_type, location, created_at.
  - `Survey`: ID, asset_id, analysis_id, filename, image_data/url, status, severity, crack_type, estimated_width, max_aperture_mm, affected_area, confidence, inference_time_ms, standard_code, calibration_json, caliper_samples_json, metrics_json, assessment_json, recommendation, created_at.
  - `DefectFissure`: ID, survey_id, polygon_json, bounding_box_json, confidence, aperture_mm.

### 2. CRUD Endpoints (`backend/app/api/`)
- `GET /api/surveys`: Query surveys with filters (`severity`, `standard_code`, `limit`, `offset`).
- `GET /api/surveys/{survey_id}`: Fetch detailed survey by ID.
- `POST /api/surveys`: Create/persist a survey record.
- `DELETE /api/surveys/{survey_id}`: Remove survey record.
- `GET /api/assets`: List unique infrastructure assets.
- `POST /api/assets`: Register a new infrastructure asset.

### 3. Server-Side PDF Report Generator (`backend/app/services/pdf_generator.py`)
- ReportLab Platypus document layout:
  - Official SCAR Header & Department Audit metadata
  - Structural asset metadata table
  - Embedded inspection image with defect annotations
  - Multi-code standard compliance evaluation table
  - Localized caliper sampling table with exceedance indicators
  - ASTM C881 remediation recommendation and structural disclaimer
  - Professional Engineer (PE/SE) seal & signature block
- Endpoints:
  - `GET /api/surveys/{survey_id}/pdf`: Generate and download PDF for saved survey.
  - `POST /api/surveys/export-pdf`: Generate PDF directly from posted inspection data.

### 4. Batch Analysis Endpoint (`POST /analyze/batch`)
- Multi-file multipart handler for high-volume uploads.
- Parallel or sequential worker execution using AnyIO thread offloading.
- Aggregated batch response with individual results and overall inspection summary.

### 5. Frontend Integration
- Update `AnalysisResults.tsx`: Direct "Download Official PDF" button calling the backend PDF service.
- Update `AnalysisHistory.tsx`: Connect to backend SQLite `/api/surveys` endpoints with live search, filters, delete, and PDF export.
- Update `ImageUploader.tsx`: Multi-image drag & drop / selection with batch processing progress tracker.

### 6. Verification & Automated Tests
- Database unit and migration tests.
- PDF generation tests verifying valid PDF byte stream with ReportLab.
- Batch analysis endpoint tests with multiple synthetic images.
- Frontend build verification.
