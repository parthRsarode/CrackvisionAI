# CrackVision AI

AI-powered civil infrastructure crack detection web application.

## Overview

CrackVision AI is an academic project that provides an intuitive web interface for detecting cracks in civil infrastructure such as walls, roads, beams, and concrete surfaces. The application uses a mock AI analyzer (designed for easy replacement with YOLOv8) to provide instant feedback on crack detection, severity, and recommended actions.

## Features

- **Image Upload**: Drag-and-drop or click-to-upload interface with validation
- **AI Analysis**: Real-time crack detection simulation with realistic results
- **Visual Results**: Original image with simulated crack highlight overlays
- **Detailed Metrics**: Confidence scores, crack type, severity, width estimation, affected area
- **Professional Recommendations**: Actionable insights based on analysis results
- **Analysis History**: Persistent history using browser localStorage
- **Responsive Design**: Works on mobile and desktop devices
- **Accessibility**: Keyboard navigation, ARIA labels, focus states
- **Report Generation**: Printable HTML report view

## Architecture

```
crackvision-ai/
├── frontend/                 # React + TypeScript + Vite application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API service layer
│   │   ├── types/            # TypeScript interfaces
│   │   ├── App.tsx           # Root application component
│   │   └── main.tsx          # Application entry point
│   ├── public/               # Static assets
│   ├── index.html            # HTML template
│   ├── package.json          # Frontend dependencies
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   └── vite.config.ts        # Vite build configuration
│
└── backend/                  # Python + FastAPI application
    ├── app/
    │   ├── main.py           # FastAPI application entry point
    │   ├── schemas.py        # Pydantic data models
    │   ├── services/         # Business logic
    │   │   └── crack_analyzer.py  # Mock AI analyzer (YOLOv8 ready)
    │   └── utils/            # Utility functions
    ├── requirements.txt      # Python dependencies
    └── ...                   # Configuration files
```

## Technology Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library

### Backend
- **Python 3.8+** - Programming language
- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

## Getting Started

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+ and pip

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd crackvision-ai/backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# In a new terminal
cd crackvision-ai/frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## API Documentation

### Health Check
```
GET /health
```
Returns server status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-09-23T10:30:00.000Z"
}
```

### Image Analysis
```
POST /analyze
```
Analyzes an uploaded image for cracks.

**Parameters:**
- `file`: multipart/form-data image (JPG, JPEG, PNG, WEBP, max 5MB)

**Response:**
```json
{
  "analysis_id": "ana_12345_1695432000",
  "status": "crack_detected",
  "confidence": 92.4,
  "crack_type": "Diagonal surface crack",
  "severity": "medium",
  "estimated_width": "0.3 - 0.7 mm",
  "affected_area": "4.8%",
  "recommendation": "Schedule a detailed visual inspection and seal the surface crack if confirmed.",
  "inspection_note": "This is an AI-assisted preliminary assessment and does not replace a qualified civil or structural engineer.",
  "annotated_image_note": "Crack regions highlighted in red",
  "created_at": "2026-09-23T10:30:00.000Z"
}
```

## Mock Analyzer Explanation

The backend includes a mock crack analyzer in `backend/app/services/crack_analyzer.py` that generates deterministic results based on image filename and file properties. This allows for consistent testing without requiring actual AI models or external APIs.

### How the Mock Works
1. Creates a deterministic seed from the filename and file size
2. Uses this seed to generate consistent analysis results
3. Simulates realistic crack detection scenarios:
   - ~70% chance of detecting a crack
   - Various crack types (diagonal, vertical, horizontal, map cracking, etc.)
   - Severity levels (low, medium, high) with appropriate distributions
   - Realistic confidence scores, width estimates, and affected areas
   - Appropriate recommendations based on severity

### Deterministic Behavior
The same image will always produce the same analysis result, making testing and demonstrations consistent.

## Replacing Mock Analyzer with YOLOv8

The mock analyzer is designed to be easily replaced with a real YOLOv8/segmentation model. Here's how to integrate it:

### 1. Install Required Dependencies
```bash
pip install ultralytics opencv-python numpy
```

### 2. Modify `crack_analyzer.py`:
```python
# Add imports
from ultralytics import YOLO
import cv2
import numpy as np

class CrackAnalyzer:
    def __init__(self):
        # Load YOLOv8 model (train your own or use pre-trained)
        self.model = YOLO('path/to/yolov8_crack_model.pt')
        # Optional: Load calibration reference for width calculation
        self.calibration_reference = None
    
    async def analyze(self, file_bytes: bytes, filename: str = None) -> Dict[str, Any]:
        # Convert bytes to image
        nparr = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Run YOLOv8 inference
        results = self.model(image)
        
        # Process results
        # Extract masks, boxes, confidence scores
        # Calculate crack width using calibration reference (if available)
        # Generate measurements and recommendations
        
        # Return structured analysis result
        return {
            # ... same structure as mock analyzer
        }
```

### 3. Key Integration Points
- **Model Inference**: Replace mock logic with actual YOLOv8 predictions
- **Segmentation Masks**: Use model outputs to create accurate crack overlays
- **Width Calculation**: Implement crack width measurement using known references
- **Confidence Scores**: Extract and utilize model confidence values
- **Post-processing**: Filter detections, apply NMS, validate results

## Known Limitations

1. **Mock Analyzer**: Current implementation uses simulated results, not actual computer vision
2. **No Authentication**: Designed for single-user academic use
3. **Browser Storage**: History stored only in localStorage (cleared when browser data is cleared)
4. **File Size Limit**: 5MB maximum upload size
5. **Supported Formats**: Only JPG, JPEG, PNG, WEBP images
6. **No Cloud Integration**: All processing happens locally

## Safety Disclaimer

⚠️ **IMPORTANT**: CrackVision AI is an educational project and provides AI-assisted preliminary assessment only. 

**NOTICE**: This tool does NOT replace professional engineering judgment. All analysis results should be reviewed by qualified civil or structural engineers before making any safety-related decisions or conducting repairs.

The developers assume no liability for misuse of this application or reliance on its outputs for critical infrastructure decisions.

## Future Improvements

- Live camera capture for real-time analysis
- Integration of YOLOv8 crack segmentation model
- Crack width estimation using reference markers (coin, ruler, etc.)
- GPS location tagging for geospatial analysis
- PDF report generation with professional formatting
- Cloud database and multi-user history
- Engineer dashboard for team collaboration
- Video analysis capabilities
- Batch processing of multiple images
- Advanced preprocessing (lighting correction, perspective transformation)

## License

This project is created for educational purposes. Feel free to use and modify for learning.

---

**CrackVision AI** - Empowering civil infrastructure inspection through accessible AI technology.
