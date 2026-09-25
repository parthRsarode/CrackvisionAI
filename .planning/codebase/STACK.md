# Technology Stack

## Core Architecture & Languages

- **Frontend Language**: TypeScript (`^4.9.3`), JavaScript (ES2022)
- **Frontend UI Framework**: React (`^18.2.0`), React DOM (`^18.2.0`)
- **Frontend Build Tool & Dev Server**: Vite (`^4.5.14`) with `@vitejs/plugin-react` (`^4.0.0`)
- **Backend Language**: Python (`3.13.2`)
- **Backend Web Framework**: FastAPI (`>=0.141.1`)
- **Backend ASGI Server**: Uvicorn (`>=0.53.0`)
- **Data Validation & Schemas**: Pydantic v2 (`>=2.13.5`)

## Frontend Libraries & Dependencies

- **Routing**: `react-router-dom` (`^6.30.6`)
- **Icons**: `lucide-react` (`^0.263.1`)
- **Drag & Drop**: Native HTML5 Drag and Drop events (`onDragOver`, `onDragEnter`, `onDragLeave`, `onDrop`), supported by legacy `react-dnd` / `react-dnd-html5-backend` (`^16.0.1`)
- **Styling**:
  - `tailwindcss` (`^3.2.7`)
  - `postcss` (`^8.4.21`) with `postcss.config.cjs`
  - `autoprefixer` (`^10.4.13`)
- **Theme & Design System**: Authentic Civil Engineering CAD & Field Terminal aesthetic (Structural Steel Navy `#0f1f38`, Construction Safety Orange `#ea580c`, Safety Amber `#d97706`, drafting grid pattern)

## Backend Libraries & Dependencies

- **API Framework**: `fastapi` (`^0.141.1`), `starlette` (`^1.7.0`)
- **Multipart Uploads**: `python-multipart` (`^0.0.32`)
- **Data Schemas**: `pydantic` (`^2.13.5`), `pydantic-core` (`^2.46.5`)
- **Scientific & Image Processing**:
  - `numpy` (`^2.5.3`) - statistical operations, matrix sampling
  - `pillow` (`^12.3.0`) - image decoding, format validation, dimensions
- **Asynchronous Runtime**: `anyio` (`^4.15.1`)

## Environment & Tooling

- **Node.js**: Node 18+ / npm
- **Python**: Python 3.13 in isolated virtualenv (`backend/venv`)
- **Default Frontend Port**: `3001` (configured in `vite.config.ts` to avoid conflict with standard port 3000)
- **Default Backend Port**: `8000` (FastAPI / Uvicorn)
- **Local Persistence**: Browser `localStorage` (key: `crackvision-history`, up to 50 items)
