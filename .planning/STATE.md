# Project State & Memory

## Current Status

- **Project**: CrackVision AI (Civil Infrastructure Crack Assessment System)
- **Active Milestone**: Milestone 1 (v1.0 Operational) Complete; Ready for Milestone 2 Planning
- **Last Updated**: 2026-09-25

## Locked Architectural Decisions

- **DEC-001**: Backend built on Python 3.13 + FastAPI with Uvicorn ASGI server on port 8000.
- **DEC-002**: Frontend built on React 18 + TypeScript + Vite running on port 3001 to prevent port conflicts with local dev servers on port 3000.
- **DEC-003**: Theme aligned to authentic Civil Engineering CAD drafting aesthetic (Steel Navy `#0f1f38`, Safety Orange `#ea580c`, technical drafting grid) complying with ACI 224R-01.
- **DEC-004**: Decoupled `CrackAnalyzer` service in backend allows direct model drop-in (YOLOv8) without altering the API contract.

## Service Status

| Service | Port | Endpoint | Status |
|---|---|---|---|
| **FastAPI Backend** | 8000 | `http://localhost:8000` | Operational |
| **Vite Frontend** | 3001 | `http://localhost:3001` | Operational |
| **Swagger API Docs** | 8000 | `http://localhost:8000/docs` | Available |
