# Codebase Onboarding Summary: CrackVision AI

## Onboarding Overview

The CrackVision AI codebase has been mapped, analyzed, and ingested into the GSD planning system.

- **Domain**: Civil & Structural Health Monitoring (SHM), Concrete Crack Detection & Aperture Survey.
- **Standards Implemented**: ACI 224R-01, ASTM C823, ASTM C881, AASHTO MBE, FHWA BIRM.
- **Repository Type**: Monorepo with independent `frontend/` and `backend/` packages.

## Codebase Map Inventory

All 7 core codebase documents have been generated in `.planning/codebase/`:

1. [`STACK.md`](../codebase/STACK.md) — React 18, TypeScript, Vite, Tailwind CSS, FastAPI, Uvicorn, Pydantic v2, NumPy, Pillow.
2. [`INTEGRATIONS.md`](../codebase/INTEGRATIONS.md) — REST API endpoints (`/health`, `/analyze`), CORS configuration, localStorage schema, CSV export.
3. [`ARCHITECTURE.md`](../codebase/ARCHITECTURE.md) — Single-page dashboard architecture, component tree, and inference adapter pipeline.
4. [`STRUCTURE.md`](../codebase/STRUCTURE.md) — Directory layout and component inventory.
5. [`CONVENTIONS.md`](../codebase/CONVENTIONS.md) — Coding standards, typing conventions, damage grade classifications.
6. [`TESTING.md`](../codebase/TESTING.md) — Build scripts, endpoint tests, interactive validation scenarios.
7. [`CONCERNS.md`](../codebase/CONCERNS.md) — Technical debt, mock-to-YOLOv8 replacement path, optical spatial calibration.

## Planning Artifacts Initialized

- [`PROJECT.md`](../PROJECT.md) — Project vision, core capabilities, and constraints.
- [`REQUIREMENTS.md`](../REQUIREMENTS.md) — 12 completed v1.0 requirements + future milestone requirements.
- [`ROADMAP.md`](../ROADMAP.md) — Completed Milestone 1 + Planned Milestone 2 (Real YOLOv8, Optical Caliper, Database).
- [`STATE.md`](../STATE.md) — Project status, ports, and architectural decision records.
- [`config.json`](../config.json) — GSD workflow preferences.

## Recommended Next Steps

- To check overall project health and statistics:
  Run `/gsd-progress` or `/gsd-stats`.
- To begin planning the next feature milestone (e.g. YOLOv8 model integration or interactive millimeter caliper calibration):
  Run `/gsd-plan-phase 3`.
