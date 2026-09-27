# Project State & Memory

## Current Status

- **Project**: CrackVision AI (Civil Infrastructure Crack Assessment System)
- **Active Milestone**: Milestone 2 (v2.0 Real Computer Vision & Metric Calibration)
- **Current Phase**: Phase 03 (YOLOv8 Segmentation Pipeline Integration) — Ready for Execution (2 plans, 2 waves)
- **Last Updated**: 2026-09-28

## Locked Architectural Decisions

- **DEC-001**: Backend built on Python 3.13 + FastAPI with Uvicorn ASGI server on port 8000.
- **DEC-002**: Frontend built on React 18 + TypeScript + Vite running on port 5173 to prevent port conflicts with local dev servers on ports 3000/3001.
- **DEC-003**: Theme aligned to authentic Civil Engineering CAD drafting aesthetic (Steel Navy `#0f1f38`, Safety Orange `#ea580c`, technical drafting grid) complying with ACI 224R-01.
- **DEC-004**: Decoupled `CrackAnalyzer` service in backend allows direct model drop-in (YOLOv8) without altering the API contract.

## Service Status

| Service | Port | Endpoint | Status |
|---|---|---|---|
| **FastAPI Backend** | 8000 | `http://localhost:8000` | Operational |
| **Vite Frontend** | 5173 | `http://localhost:5173` | Operational |
| **Swagger API Docs** | 8000 | `http://localhost:8000/docs` | Available |
