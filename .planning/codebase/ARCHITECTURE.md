# System Architecture

## Architecture Overview

CrackVision AI is built with a decoupled client-server architecture tailored for civil infrastructure inspection, structural health monitoring, and damage assessment:

```
[ Client Browser (React + TypeScript + Vite) ]
                    │
                    ▼  (HTTP REST / Multipart Uploads via api.ts)
[ ASGI Backend (FastAPI + Uvicorn) ]
                    │
                    ▼
[ Services Layer (CrackAnalyzer Adapter) ]
                    │
      ┌─────────────┴─────────────┐
      ▼                           ▼
[ Mock Deterministic Engine ]  [ YOLOv8 / DeepLabV3+ (Planned) ]
```

## Component Architecture (Frontend)

The frontend is a single-page application centered around `Dashboard.tsx`:

```
App.tsx (ErrorBoundary + DndProvider + BrowserRouter)
  └── Dashboard.tsx
        ├── Navbar.tsx (Live Health Indicator, Navigation, Modals)
        ├── Hero.tsx (Scope, Standards, Benchmark Asset Selector)
        ├── ImageUploader.tsx (Asset Metadata Form + CAD Dropzone)
        │     └── data/sampleImages.ts (Instant SVG-to-JPEG Benchmark Assets)
        ├── AnalysisLoader.tsx (Diagnostic Processor Step Tracker)
        ├── AnalysisResults.tsx (SCAR Condition Report, ACI Matrix, Print Layout)
        │     ├── SeverityBadge.tsx (Grade 1/2/3 Damage Badges)
        │     ├── ImagePreview.tsx (Contour View, Split Comparison)
        │     └── CrackComparatorCard.tsx (ACI Optical Millimeter Scale Overlay)
        ├── AnalysisHistory.tsx (Civil Survey Logbook, Search, Filters, CSV Export)
        ├── HowItWorksModal.tsx (Engineering Methodology Walkthrough)
        ├── AboutModal.tsx (ACI 224R / ASTM C823 Reference Guide)
        └── Footer.tsx (Technical Standards & PE Compliance Disclaimer)
```

## Data Flow & State Management

1. **Asset Selection or File Upload**:
   - The user selects a pre-calibrated sample asset (`SAMPLE_IMAGES`) or uploads a local field photograph.
   - The user selects structural component metadata (e.g. Bridge Pier, Prestressed Girder) and ACI exposure condition.
2. **Inference Request**:
   - `handleAnalyze(file)` triggers `analyzeImage(file)` in `services/api.ts`.
   - `isLoading` activates `AnalysisLoader.tsx`, presenting the 4-phase diagnostic processing pipeline.
3. **Backend Processing**:
   - `app/main.py` validates file type (JPEG, PNG, WEBP) and size.
   - `crack_analyzer.py` calculates a deterministic seed from the image hash, generating realistic crack morphology, aperture range (mm), surface area (%), and ACI-aligned engineering recommendations.
4. **Result Presentation**:
   - The result is rendered in `AnalysisResults.tsx` as a formal Structural Condition Assessment Report (SCAR).
   - `ImagePreview.tsx` enables orthographic inspection with an ACI Crack Width Comparator Card overlay.
   - The assessment is saved to browser `localStorage` and populated into the Survey Logbook (`AnalysisHistory.tsx`).
