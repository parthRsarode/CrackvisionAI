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

## Milestone 2: Real Computer Vision & Metric Calibration (v2.0) — PLANNED

- **Phase 03: YOLOv8 Segmentation Pipeline Integration (COMPLETED)**
  - Integrated Ultralytics YOLOv8 segmentation model with retina_masks=True.
  - Output exact polygonal mask coordinates and pixel confidence scores from `/analyze`.
  - Render true segmented defect masks on frontend canvas.
- **Phase 04: Interactive Caliper & Spatial Scale Calibration**
  - Add two-point millimeter optical calibration on the image viewer.
  - Add interactive caliper tool for localized crack width sampling.
- **Phase 05: Persistent Database & Formal PDF Generation**
  - Introduce SQLite/PostgreSQL persistence for assets and inspections.
  - Implement server-side PDF generation for archival inspection reports.
  - Support multi-image batch analysis.
