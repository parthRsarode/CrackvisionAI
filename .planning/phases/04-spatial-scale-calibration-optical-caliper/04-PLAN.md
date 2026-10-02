# Phase 04 Plan: Interactive Caliper & Spatial Scale Calibration

## Overview
Implement two-point millimeter optical calibration, automated ArUco fiducial marker scale detection, and an interactive digital caliper tool for localized crack width sampling.

## Requirements Covered
- **REQ-3.1**: Interactive two-point millimeter scale calibration tool (user clicks two reference points and specifies real-world dimension).
- **REQ-3.2**: Automated ArUco fiducial marker detection on concrete surfaces for zero-touch metric calibration.
- **REQ-3.3**: Interactive caliper tool allowing inspectors to click anywhere on a crack to measure localized aperture width.

## Architectural Changes

### 1. Backend: Fiducial Detection & Spatial Calibration (`backend/app/services/calibration_service.py`)
- OpenCV `cv2.aruco` detector across standard dictionaries (`DICT_4X4_50`, `DICT_4X4_100`, `DICT_5X5_50`, `DICT_6X6_50`).
- Extraction of marker corners, perimeter, and mean side length in pixels.
- Calculation of exact `mm_per_pixel` scale given marker size in millimeters (default: 50.0 mm).
- Integration into `CrackAnalyzer` and `MorphometryService` to dynamically rescale all defect metrics when fiducial markers are present.
- Support for `marker_size_mm` and `manual_scale_mm_per_pixel` parameters in `/analyze`.
- New `POST /calibrate-scale` utility endpoint for instant scale recalculation.

### 2. Backend Schemas & Data Model
- New `CalibrationInfo` schema in `backend/app/schemas.py`.
- Enriched `AnalysisResponse` with calibration details and fiducial marker overlay coordinates.

### 3. Frontend: Interactive Two-Point Calibration Tool (`ImagePreview.tsx`)
- CAD drafting scale mode in the inspection toolbar.
- Point A and Point B crosshair placement with live pixel distance tracking line.
- Known dimension input modal with mm / inch conversion.
- Live recalculation of all crack widths, lengths, areas, and ACI/Eurocode/IS compliance based on the new scale.
- Real-time drafting scale bar HUD at the bottom of the viewport.

### 4. Frontend: Interactive Digital Caliper Tool (`ImagePreview.tsx` & `CaliperTool.tsx`)
- Caliper mode in toolbar with two measurement techniques:
  1. Two-point crosshair span across crack fissure.
  2. Smart one-click polygon probe that detects local normal fissure width.
- Digital Vernier Caliper graphic overlay with millimeter aperture, pixel width, and compliance status.
- Caliper sampling table listing all placed measurements with delete and clear actions.
- Caliper sample integration into SCAR report (`AnalysisResults.tsx`) and CSV export in Field Survey Logbook.

### 5. Verification & Tests
- Unit and integration tests in `backend/tests/test_calibration.py`.
- Validation against synthetic ArUco images and uncalibrated fallback cases.
- Full frontend build verification (`npm run build`).
