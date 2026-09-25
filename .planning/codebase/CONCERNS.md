# Technical Concerns & Future Roadmap

## 1. Mock vs Real AI Model Integration

- **Current State**: `backend/app/services/crack_analyzer.py` utilizes deterministic simulation based on md5 hashing of the uploaded image bytes.
- **Risk**: For production deployment or formal civil evaluations, the mock must be swapped with a real trained segmentation model (e.g. YOLOv8x-seg trained on Crack500 / DeepCrack / SDNET2018 datasets).
- **Remediation**: The `CrackAnalyzer` service is encapsulated with clear interface boundaries (`analyze(file_bytes, filename)`), making model drop-in straightforward.

## 2. Spatial Scale & Pixel-to-mm Calibration

- **Current State**: Crack aperture width (e.g., "0.4 - 1.2 mm") is generated statistically.
- **Concern**: In real field inspections, physical scale requires Ground Sampling Distance (GSD) or an optical calibration reference marker (e.g., a coin, checkerboard scale, or optical card in the photograph).
- **Remediation**: Add a feature to allow inspectors to set optical scale (e.g., drawing a known 50mm reference bar or detecting an ArUco / QR calibration tag on the concrete).

## 3. Storage & Multi-User Collaboration

- **Current State**: History is stored exclusively in client-side browser `localStorage` (capped at 50 items).
- **Limitation**: Inspection records do not persist across devices or between multiple field surveyors.
- **Remediation**: Introduce a lightweight relational database (SQLite / PostgreSQL) with structured asset tables (`assets`, `inspections`, `defect_segments`, `remediation_records`).

## 4. Automated Segmentation Mask Generation

- **Current State**: Frontend renders a simulated SVG defect contour (`crack-pattern.svg`).
- **Target**: Backend model inference should return the actual polygon coordinates / segmentation mask PNG as base64 or URL so the true isolated crack contour is overlaid pixel-perfect onto the user's specific image.
