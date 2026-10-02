# Project Roadmap

## Milestone 1: Civil Field Inspection Terminal (v1.0) — COMPLETED

- **Phase 01: Core Platform Setup & Bug Remediation**
  - Resolved Python dependencies (`anyio`, `numpy`, `pillow`) and created venv.
  - Added FastAPI `CORSMiddleware`.
  - Configured PostCSS with Tailwind CSS.
  - Fixed JSX icon rendering crash in `Navbar.tsx` and added `ErrorBoundary` in `App.tsx`.
- **Phase 02: Civil Engineering Redesign & Standards Alignment**
  - Implemented CAD drafting grid aesthetic with structural steel navy and safety orange accents.
  - Created ACI 224R-01 Crack Comparator Scale card (0.10 mm to 3.00 mm).
  - Formatted Structural Condition Assessment Report (SCAR) with ACI compliance matrix.
  - Built Field Survey Logbook with search, severity filters, and CSV data export.
  - Added pre-calibrated benchmark asset cases and field configuration forms.

## Milestone 2: Real Computer Vision & Metric Calibration (v2.0) — COMPLETED

- **Phase 03: YOLOv8 Segmentation Pipeline Integration (COMPLETED)**
  - Integrated Ultralytics YOLOv8 segmentation model with retina_masks=True.
  - Output exact polygonal mask coordinates and pixel confidence scores from `/analyze`.
  - Render true segmented defect masks on frontend canvas.
- **Phase 04: Interactive Caliper & Spatial Scale Calibration (COMPLETED)**
  - Automated ArUco fiducial marker detection (DICT_4X4, 5X5, 6X6) for zero-touch metric calibration.
  - Interactive two-point millimeter optical datum calibration tool on the image viewer.
  - Interactive digital caliper tool with 1-click fissure probing and 2-point aperture measurement.
  - Dynamic CAD drafting scale bar HUD and localized caliper sampling log with CSV export.
- **Phase 05: Persistent Database & Formal PDF Generation (COMPLETED)**
  - Implemented SQLite relational database schema using SQLAlchemy for assets, surveys, and defect fissures.
  - Created RESTful CRUD endpoints (`/api/surveys`, `/api/assets`) with auto-persistence from `/analyze`.
  - Engineered formal Structural Condition Assessment Report (SCAR) PDF generation engine using ReportLab Platypus.
  - Multi-image batch inspection (`POST /analyze/batch`) with aggregated metrics, critical element alerts, and CAD gallery.
