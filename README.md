# CrackVision AI

> **Autonomous Civil Infrastructure Crack Segmentation, Spatial Scale Calibration, and Structural Condition Assessment Report (SCAR) System**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript)](https://www.typescriptlang.org)
[![Ultralytics](https://img.shields.io/badge/YOLOv8-Seg-FF6F00?logo=yolo)](https://github.com/ultralytics/ultralytics)
[![SQLite](https://img.shields.io/badge/SQLite-SQLAlchemy_2.0-003B57?logo=sqlite)](https://www.sqlite.org)
[![ReportLab](https://img.shields.io/badge/ReportLab-SCAR_PDF-E31B23)](https://www.reportlab.com)

---

## Overview

**CrackVision AI** is a professional-grade web application engineered for civil structural engineers, transportation departments, and field inspectors. It couples deep learning instance segmentation (**Ultralytics YOLOv8-Seg**) with subpixel fiducial calibration (**OpenCV ArUco**), normal-vector digital caliper raycasting, relational SQLite persistence, and formal PDF condition reporting according to **ACI 224R-01**, **Eurocode 2 (EN 1992)**, **IS 456:2000**, and **BS 8110**.

---

## Key Features

1. **Deep Learning Segmentation (YOLOv8-Seg)**
   - Instance segmentation with subpixel contour extraction and polygon coordinates.
   - Fallback geometric morphometry engine filtering non-crack circular artifacts (e.g. formwork tie holes).
   
2. **Spatial Scale Calibration & Optical Caliper**
   - **Zero-Touch ArUco Fiducial Detection**: Automatic millimeter-per-pixel resolution calculation using standard marker targets (`DICT_4X4`, `5X5`, `6X6`).
   - **Manual 2-Point Datum Tool**: User-defined physical distance calibration for arbitrary targets.
   - **Interactive Digital Caliper**: 1-click localized crack aperture sampling perpendicular to the fissure path with real-time code limit evaluation.

3. **Building & Asset Profile Integration**
   - **Structure Identification**: Building name/ID, building type (residential, commercial, industrial, institutional, parking structure, bridge, etc.).
   - **Dynamic Historical Age Calculation**: Age is computed automatically from construction year using the specific inspection date (not hardcoded to today's date), with support for unknown years and invalid future year flagging.
   - **Structural Typology & Material**: System (beam-column frame, shear wall, flat slab, masonry, etc.), material (reinforced concrete, prestressed concrete, masonry, steel, mixed), and member importance.
   - **Deterioration & Maintenance History**: Prior repairs, persistent water dampness, known settlement, and damaging events (earthquake, fire, blast, flood).
   - **Environmental Exposure**: Indoor dry, outdoor weather, persistent moisture, coastal/marine spray, industrial/chemical vapor, freeze-thaw.

4. **Transparent Age-Aware Condition Assessment Engine**
   - **Decoupled from Simplistic Multipliers**: Building age serves as contextual durability evidence rather than an arbitrary severity multiplier (a new building with severe shear cracking near supports is not called safe, and an older building with hairline shrinkage is not called dangerous).
   - **Early-Age ($\le 5$ years) Construction Defect Detection**:
     - Grounded in **ACI 224.1R-07** (Sections 1.2–1.3), **ACI CODE-562-25** (Section 6.2), **IS 456:2000 Cl. 11 & 35.3.2**, and **CIRIA C766**.
     - When early-age structures exhibit elevated or severe cracking ($\ge 0.30$ mm, shear patterns, proximity to supports, or active spalling), the engine flags `early_age_construction_defect_suspected`.
     - Automatically generates forensic action items: auditing 28-day concrete cylinder/cube tests ($f_{ck}$), formwork stripping/de-shoring dates, moist curing logs (thermal/plastic shrinkage restraint), and subgrade settlement levels.
   - **Mature Structures (>25 years) Durability Assessment**:
     - Evaluates long-term carbonation depth exceeding cover, chloride ingress, rebar corrosion volume expansion (2–6×), and loss of structural concrete section.
   - **Component A–F Traceable Breakdown**:
     - *Component A*: AI Detection (segmentation mask and model confidence).
     - *Component B*: Surface Measurement (calibrated width, length, area, orientation, pattern).
     - *Component C*: Building and Structural Context.
     - *Component D*: Deterioration Indicators (spalling, corrosion rust, moisture ingress).
     - *Component E*: Evidence Sufficiency Audit.
     - *Component F*: Engineering Interpretation & Traceable Standards Guidance.
   - **Strict Depth Separation**: 2D optical imaging cannot measure crack depth; internal condition is strictly tracked as unverified/NDT-required without fabricating millimeter depth values.

5. **Multi-Standard Compliance Matrix**
   - Direct threshold comparison against:
     - **ACI CODE-562-25 & ACI 224R-01** (USA)
     - **IS 456:2000 & IS 15988:2013** (India)
     - **Eurocode 2 EN 1992-1-1 / EN 1992-3** (Europe)
     - **BS 8110 / BS 8500** (UK)
   - Transparent compliance statuses: *Verified*, *Provisionally Consistent*, *Requires Review*, *Potential Non-Conformance*, *Not Applicable*, *Unable to Determine*.

6. **Multi-Image Batch Inspection Survey**
   - Simultaneous multi-file upload for terrestrial or drone surveys.
   - Aggregated metrics: maximum aperture, total crack length, and critical elements flagged for priority review.
   - 1-click batch CSV export (including asset and age metadata) and individual member catalog cards.

7. **Relational Database & Formal PDF Generation**
   - SQLite persistent database storing asset profiles, survey history, and segmented fissures.
   - Immutable historical snapshots guaranteeing that editing an asset profile never mutates past inspection records.
   - Dynamic **Structural Condition Assessment Report (SCAR)** compilation via ReportLab Platypus featuring executive summaries, Building & Asset Profile tables, Age & Deterioration Context cards, orthomosaics, caliper logs, and Licensed PE/SE sign-off blocks.

---

## Quickstart Guide

For an in-depth architecture and developer guide, see **[DEVELOPER.md](DEVELOPER.md)**.

### 1. Start Backend API
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API is available at: `http://localhost:8000`
- Swagger UI Documentation: `http://localhost:8000/docs`

### 2. Start Frontend Terminal
```bash
cd frontend
npm install
npm run dev
```
- Open browser at: `http://localhost:5173` (or Vite assigned port)

---

## Automated Verification

The system includes automated test suites covering all computer vision, calibration, building age evaluation, database migrations, and PDF services:

```bash
# Run backend pytest suite (37 automated tests)
./backend/venv/bin/pytest backend/tests/ -v

# Verify frontend production build
cd frontend && npm run build
```

---

## Directory Organization

```
crackvision-ai/
├── DEVELOPER.md             # Developer architecture and onboarding guide
├── PRODUCT.md               # Product specification
├── README.md                # System overview and quickstart
├── backend/                 # FastAPI + YOLOv8 + SQLAlchemy + ReportLab
│   ├── app/                 # main.py, schemas.py, db/, services/, weights/
│   ├── data/                # SQLite storage (crackvision.db)
│   └── tests/               # 37 automated pytest unit & integration tests
│       ├── test_api.py      # Core endpoints and upload handling
│       ├── test_building_age_assessment.py # 16-scenario Building Age test suite
│       ├── test_calibration.py # ArUco fiducials and 2-point scale
│       ├── test_morphometry.py # Aspect ratio, aperture, and code limits
│       ├── test_phase5.py   # Database CRUD, CSV export, and PDF generation
│       └── test_yolo_service.py # YOLOv8 segmentation pipeline
└── frontend/                # React 18 + Vite + Tailwind CSS + Lucide
    ├── src/                 # components/, pages/, services/, types/, data/
    └── public/              # Static sample benchmark imagery
```

---

## License & Engineering Disclaimer

*CrackVision AI is designed as an AI-assisted preliminary visual assessment tool. Building age is contextual information and is not, by itself, a measure of structural safety or crack severity. All findings, severity classifications, and repair recommendations must be verified by a Licensed Professional Engineer (PE/SE) before commencing structural remediation.*
