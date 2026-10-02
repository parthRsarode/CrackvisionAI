# Project State & Memory

## Current Status

- **Project**: CrackVision AI (Civil Infrastructure Crack Assessment System)
- **Active Milestone**: Milestone 2 (v2.0 Real Computer Vision & Metric Calibration) — COMPLETED
- **Current Phase**: Phase 05 (Persistent Database, Formal PDF Generation & Batch Analysis) — COMPLETED
- **Last Updated**: 2026-10-02

## Locked Architectural Decisions

- **DEC-001**: Backend built on Python 3.13 + FastAPI with Uvicorn ASGI server on port 8000.
- **DEC-002**: Frontend built on React 18 + TypeScript + Vite running on port 5173 to prevent port conflicts with local dev servers on ports 3000/3001.
- **DEC-003**: Theme aligned to authentic Civil Engineering CAD drafting aesthetic (Steel Navy `#0f1f38`, Safety Orange `#ea580c`, technical drafting grid) complying with ACI 224R-01.
- **DEC-004**: Decoupled `CrackAnalyzer` service in backend allows direct model drop-in (YOLOv8) without altering the API contract.
- **DEC-005**: Deep learning segmentation powered by Ultralytics YOLOv8-Seg with `retina_masks=True` and AnyIO worker thread offloading.
- **DEC-006**: Geometric morphometry filters non-crack artifacts (aspect ratio < 1.3:1) and categorizes orientation and ACI 224R limits.
- **DEC-007**: Dynamic SVG polygon overlay rendering in frontend with `vector-effect="non-scaling-stroke"`.
- **DEC-008**: Optical fiducial scale detection via OpenCV `ArucoDetector` across 4x4, 5x5, 6x6 dictionaries with subpixel corner extraction and automatic `mm_per_pixel` calculation.
- **DEC-009**: Interactive localized caliper probing using normal vector raycasting across detected fissure polygons with real-time code limit evaluations.
- **DEC-010**: SQLite database engine managed via SQLAlchemy 2.0 with WAL journaling at `backend/data/crackvision.db`, providing persistent asset and survey history.
- **DEC-011**: Structural Condition Assessment Reports (SCAR) compiled dynamically using ReportLab Platypus with embedded orthomosaics, caliper logs, and PE sign-off blocks.
- **DEC-012**: High-throughput multi-image batch analysis via `POST /analyze/batch` returning aggregated survey metrics and element priority classification.

## Service Status

| Service | Port | Endpoint | Status |
|---|---|---|---|
| **FastAPI Backend** | 8000 | `http://localhost:8000` | Operational |
| **Vite Frontend** | 5173 | `http://localhost:5173` | Operational |
| **Swagger API Docs** | 8000 | `http://localhost:8000/docs` | Available |
