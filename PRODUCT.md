# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Both field inspectors capturing and analyzing images on-site via mobile devices, and structural engineers analyzing inspection photos on desktop back in the office.

## Product Purpose
An AI-assisted preliminary assessment tool for civil infrastructure inspection. It detects concrete/asphalt cracks, estimates aperture width, and evaluates structural severity against global benchmarks (ACI 224R, IS 456, Eurocode 2, BS 8110). 

## Positioning
A zero-cost, CPU-friendly vision architecture combining YOLOv8 instance segmentation with classical CV extraction. It provides multi-code standard compliance cards and generates Structural Condition Assessment Reports (SCAR).

## Operating Context
Used during physical field surveys (Field Survey Logbook) and structural condition audits. Engineers capture photos of cracks (e.g., bridge girders, concrete walls) and upload them for immediate analysis. Requires explicit engineering safety disclaimers.

## Capabilities and Constraints
- Deterministic/calibrated optical gauge readings (0.15mm - 2.50mm).
- Must maintain isolated ports: FastAPI backend (8000) and Vite frontend (5173).
- Explicitly limited to AI-assisted preliminary assessment; never claims a building is safe.

## Brand Commitments
Name: CrackVision AI
Mission: Empowering civil infrastructure inspection through accessible AI technology.

## Evidence on Hand
- Proven detection recall (100%) and false-positive precision (100%) on structural benchmark cases.
- Existing CAD UI layout, SCAR report format, and Field Survey Logbook.

## Product Principles
- **Engineering Precision**: The UI must serve accurate, verifiable data.
- **Strict Compliance Context**: Every assessment must be framed by selected structural codes.
- **Safety First**: Disclaimers and limitations must be clearly visible, preventing over-reliance on AI outputs without professional verification.
