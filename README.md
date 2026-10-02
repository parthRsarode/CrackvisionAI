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

3. **Multi-Standard Compliance Matrix**
   - Direct threshold comparison against:
     - **ACI 224R-01 / CODE-562** (USA)
     - **Eurocode 2 EN 1992-1-1** (Europe)
     - **IS 456:2000 Table 2** (India)
     - **BS 8110 / BS 8500** (UK)
   - ACI 224R optical comparator scale card (0.10 mm to 3.00 mm).

4. **Multi-Image Batch Inspection Survey**
   - Simultaneous multi-file upload for terrestrial or drone surveys.
   - Aggregated metrics: maximum aperture, total crack length, and critical elements flagged for priority review.
   - 1-click batch CSV export and individual member catalog cards.

5. **Relational Database & Formal PDF Generation**
   - SQLite persistent database storing asset tags, inspection surveys, and segmented fissures.
   - Dynamic **Structural Condition Assessment Report (SCAR)** compilation via ReportLab Platypus with embedded orthomosaics, caliper logs, and Licensed PE/SE sign-off blocks.

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
- Open browser at: `http://localhost:5173`

---

## Automated Verification

The system includes automated test suites covering all computer vision, calibration, database, and PDF services:

```bash
# Run backend pytest suite (21 tests)
./backend/venv/bin/pytest backend/tests

# Verify frontend build
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
│   └── tests/               # 21 automated pytest unit & integration tests
└── frontend/                # React 18 + Vite + Tailwind CSS + Lucide
    ├── src/                 # components/, pages/, services/, types/, data/
    └── public/              # Static sample benchmark imagery
```

---

## License & Engineering Disclaimer

*CrackVision AI is designed as an AI-assisted preliminary visual assessment tool. All findings, severity classifications, and repair recommendations must be verified by a Licensed Professional Engineer (PE/SE) before commencing structural remediation.*
