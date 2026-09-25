# Testing & Quality Verification

## Build & Static Verification

- **Frontend Compilation**:
  ```bash
  cd frontend
  npm run build
  ```
  Executes `vite build`, type-checking all TSX components and compiling Tailwind CSS via PostCSS.
- **Backend Import Validation**:
  ```bash
  cd backend
  ./venv/bin/python3 -c "import app.main; print('Backend loaded cleanly')"
  ```

## API & Runtime Testing

- **Backend Health Check**:
  ```bash
  curl -s http://localhost:8000/health
  ```
  Expected: `{"status":"healthy","timestamp":"..."}`
- **Analysis Endpoint (Multipart POST)**:
  ```bash
  curl -s -X POST http://localhost:8000/analyze -F "file=@frontend/test_image.jpg"
  ```
- **CORS Preflight Verification**:
  ```bash
  curl -s -I -X OPTIONS http://localhost:8000/analyze \
    -H "Origin: http://localhost:3001" \
    -H "Access-Control-Request-Method: POST"
  ```

## User Acceptance / Interactive Testing Scenarios

1. **Pre-calibrated Asset Benchmark**:
   - Click any sample card on the Hero or dropzone (*Concrete Wall*, *Highway Asphalt*, *Bridge Girder*).
   - Verify diagnostic processor phases animate through completion.
   - Verify SCAR report displays correct crack morphology and aperture metrics.
2. **Interactive Optical Measurement**:
   - Toggle "Show ACI Comparator Card" to verify millimeter graduation lines appear next to the orthomosaic.
   - Toggle view modes (*Defect Contour*, *Split Verification*, *Raw Surface*).
3. **Report Generation**:
   - Click "Print Official Structural Report" to verify print preview renders clean black-and-white formatting with PE stamp and signature lines.
4. **Logbook Audit & Export**:
   - Verify completed assessment is recorded in the Survey Logbook.
   - Click "Export CSV" and verify downloaded CSV schema.
