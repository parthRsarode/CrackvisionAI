# Project Directory Structure

```
crackvision-ai/
├── .git/                      # Git repository tracking
├── .gitignore                 # Ignore rules (node_modules, venv, logs, build dist)
├── README.md                  # Project overview and run instructions
│
├── backend/                   # Python FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI entry point, endpoints, CORS middleware
│   │   ├── schemas.py         # Pydantic v2 data models (AnalysisResponse)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── crack_analyzer.py # Analysis service (seeded mock / YOLOv8 adapter)
│   │   └── utils/
│   │       └── __init__.py
│   ├── requirements.txt       # Python dependencies (fastapi, uvicorn, numpy, pillow)
│   └── venv/                  # Local Python virtual environment
│
├── frontend/                  # React + TypeScript + Vite Frontend
│   ├── public/
│   │   └── crack-pattern.svg  # Default defect segmentation overlay texture
│   ├── src/
│   │   ├── assets/            # Static assets
│   │   ├── components/        # Reusable UI components
│   │   │   ├── AboutModal.tsx            # ACI / ASTM technical standards modal
│   │   │   ├── AnalysisHistory.tsx       # Survey logbook, search, filters, CSV export
│   │   │   ├── AnalysisLoader.tsx        # Diagnostic pipeline processing tracker
│   │   │   ├── AnalysisResults.tsx       # SCAR report, ACI compliance matrix
│   │   │   ├── CrackComparatorCard.tsx   # ACI optical millimeter scale card
│   │   │   ├── EmptyState.tsx            # Placeholder state component
│   │   │   ├── Footer.tsx                # Technical standards & PE notices
│   │   │   ├── Hero.tsx                  # Field terminal scope & sample test cases
│   │   │   ├── HowItWorksModal.tsx       # Computer vision methodology walkthrough
│   │   │   ├── ImagePreview.tsx          # Orthomosaic viewer with comparator toggle
│   │   │   ├── ImageUploader.tsx         # CAD dropzone with asset metadata form
│   │   │   ├── Navbar.tsx                # Header bar, live health indicator
│   │   │   └── SeverityBadge.tsx         # Grade 1/2/3 damage classification badge
│   │   ├── data/
│   │   │   └── sampleImages.ts           # Pre-calibrated benchmark asset generator
│   │   ├── pages/
│   │   │   └── Dashboard.tsx             # Root page component coordinating workflow
│   │   ├── services/
│   │   │   └── api.ts                    # REST client for backend API communication
│   │   ├── types/
│   │   │   └── analysis.ts               # TypeScript interfaces (AnalysisResult, etc.)
│   │   ├── App.tsx                       # Root component with ErrorBoundary & Dnd
│   │   ├── index.css                     # CAD grid background, printing stylesheet
│   │   └── main.tsx                      # Vite React DOM entry point
│   ├── index.html             # HTML entry template
│   ├── package.json           # Node dependencies and build scripts
│   ├── package-lock.json
│   ├── postcss.config.cjs     # PostCSS configuration for Tailwind CSS
│   ├── tailwind.config.js     # Tailwind configuration with Civil Engineering palette
│   └── vite.config.ts         # Vite server configuration (port: 3001)
│
└── .planning/                 # GSD Project Management & Intelligence
    ├── codebase/              # 7 Codebase mapping documents
    └── onboarding/            # Onboarding summary & status index
```
