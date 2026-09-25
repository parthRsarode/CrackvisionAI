# CrackVision AI — Project Overview

## Vision

CrackVision AI is a specialized civil infrastructure health monitoring and crack assessment platform. It enables civil engineers, DOT inspectors, and asset managers to detect, segment, and quantify structural surface fissures across concrete and asphalt assets (such as bridge piers, precast girders, retaining walls, and highway pavements) in compliance with ACI 224R-01 permissible limit tables.

## Core Capabilities (v1.0 Operational)

- **Autonomous Surface Scan & Morphometry**: Categorizes cracks (vertical shrinkage, diagonal shear, horizontal settlement, map cracking, spalling, flexural distress).
- **Field Asset Configuration**: Captures structural component type, ACI 224R environmental exposure category, and station/chainage IDs.
- **ACI 224R-01 Crack Comparator Scale**: An interactive digital version of physical optical comparator cards with calibrated millimeter graduations (0.10 mm to 3.00 mm).
- **Orthomosaic Inspection Modes**: Defect contour overlay, side-by-side comparison, and raw surface inspection.
- **Structural Condition Assessment Report (SCAR)**: Automated reporting featuring quantitative metrics, ACI compliance matrix, ASTM C881 repair protocol, and official PE stamp signature blocks for printouts.
- **Field Survey Logbook**: Local inspection records with multi-level severity filtering, search, and CSV export.
- **Pre-calibrated Benchmark Assets**: 1-click test cases for instant demonstration and testing.

## Tech Stack Summary

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React
- **Backend**: FastAPI, Uvicorn, Pydantic v2, NumPy, Pillow, AnyIO
- **Standards & Codes**: ACI 224R-01, ASTM C823, ASTM C881, AASHTO MBE, FHWA BIRM

## Key Constraints

- Current analysis service operates as a high-fidelity seeded deterministic simulation, architected for direct replacement with YOLOv8-Seg or DeepLabV3+.
- Storage is currently browser-local (`localStorage`), suitable for single-device field screening.
