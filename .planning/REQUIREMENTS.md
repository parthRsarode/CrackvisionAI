# Project Requirements

## Completed Requirements (v1.0 MVP)

- [x] **REQ-1.1**: FastAPI backend server with CORS middleware, asynchronous request handlers, and `/health` verification.
- [x] **REQ-1.2**: Image analysis endpoint (`POST /analyze`) handling multipart/form-data with file type and size validation.
- [x] **REQ-1.3**: Pydantic v2 data models for rigorous schema validation.
- [x] **REQ-1.4**: React 18 + Vite frontend with Tailwind CSS styling and PostCSS configuration.
- [x] **REQ-1.5**: Civil Engineering CAD drafting aesthetic with structural steel navy and safety orange accents.
- [x] **REQ-1.6**: Field asset metadata input form (Component Type, ACI Exposure, Stationing).
- [x] **REQ-1.7**: Pre-calibrated benchmark assets (Concrete Wall, Highway Asphalt, Bridge Girder).
- [x] **REQ-1.8**: ACI 224R-01 Crack Comparator Scale card with calibrated millimeter lines (0.10mm - 3.00mm).
- [x] **REQ-1.9**: Visual inspection modes (Defect contour, split verification, raw surface).
- [x] **REQ-1.10**: Structural Condition Assessment Report (SCAR) with ACI compliance matrix, ASTM C881 repair protocol, and printable PE signoff block.
- [x] **REQ-1.11**: Field Survey Logbook with local storage persistence, search, severity filters, and CSV export.
- [x] **REQ-1.12**: Runtime ErrorBoundary and live backend health monitor.

## Future Milestone Requirements (v2.0+)

### Phase 1: Real AI Segmentation Model (YOLOv8-Seg)
- [x] **REQ-2.1**: Integrate PyTorch / Ultralytics YOLOv8 segmentation model weights (`yolov8s-seg` / `crack_yolov8s_seg.pt` trained on Crack500/SDNET2018).
- [x] **REQ-2.2**: Return exact polygonal segmentation masks and bounding boxes from `/analyze`.
- [x] **REQ-2.3**: Render true segmented mask overlays on the frontend canvas instead of default SVG textures.

### Phase 2: Spatial Scale Calibration & Optical Caliper
- [ ] **REQ-3.1**: Interactive two-point millimeter scale calibration tool (user clicks two points and specifies real-world distance in mm/inches).
- [ ] **REQ-3.2**: Automated ArUco / AprilTag fiducial marker detection on concrete surfaces for zero-touch metric calibration.
- [ ] **REQ-3.3**: Interactive caliper tool allowing inspectors to click anywhere on a crack to measure localized aperture width.

### Phase 3: Centralized Database & Team Collaboration
- [ ] **REQ-4.1**: SQLite / PostgreSQL database schema for assets, surveys, and defect records.
- [ ] **REQ-4.2**: RESTful CRUD endpoints for historical inspection management.
- [ ] **REQ-4.3**: PDF export generation on the backend (using ReportLab or WeasyPrint).
- [ ] **REQ-4.4**: Batch image inspection upload for high-volume drone and terrestrial surveys.
