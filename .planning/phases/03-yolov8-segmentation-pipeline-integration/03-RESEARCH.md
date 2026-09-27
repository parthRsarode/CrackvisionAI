# Phase 03 — Technical Research: YOLOv8 Segmentation Pipeline Integration

<summary>
## Executive Summary

Phase 03 replaces the v1.0 deterministic seed simulation with a real, high-performance computer vision segmentation pipeline. The target model is Ultralytics YOLOv8-Seg (specifically `yolov8s-seg` / fine-tuned crack weights from Crack500 / SDNET2018), outputting precise polygonal coordinates, bounding boxes, and confidence scores.

Key architectural requirements:
1. **Thread-Safe Asynchronous Execution**: PyTorch inference is compute-intensive and synchronous; it must be offloaded to worker threads via `anyio.to_thread.run_sync` to protect FastAPI's event loop.
2. **High-Fidelity Contour Extraction**: By default, YOLOv8 generates masks on a downsampled 160x160 prototype grid. We must enforce `retina_masks=True` to preserve sub-millimeter hairline crack fissures.
3. **Structured API Contract**: The backend must emit both pixel coordinates (`masks.xy`) and normalized `[0, 1]` coordinates (`masks.xyn`) inside an extended Pydantic v2 `AnalysisResponse` schema that maintains backward compatibility.
4. **Resilient Fallback**: If PyTorch model weights are unavailable or GPU/MPS initialization fails, the service gracefully degrades to `FallbackCrackAnalyzer` without returning 500 errors.
5. **Frontend Canvas Rendering**: The React frontend (`InspectionViewport.tsx`) must parse polygon arrays and render SVG `<polygon>` vectors overlaying the image viewport with interactive hover, inspection modes, and ACI 224R comparator alignment.
</summary>

<standard_stack>
## Standard Stack

### Backend Dependencies
- **`ultralytics>=8.3.0`**: Core deep learning segmentation framework providing `YOLO` engine, pre/post-processing, and polygon raster-to-vector extraction.
- **`torch>=2.2.0` & `torchvision>=0.17.0`**: Underlying tensor engine supporting Apple Silicon Metal Performance Shaders (`mps`) and CPU fallback.
- **`opencv-python-headless>=4.8.0`**: Computer vision primitives for image transformations, morphological operations, and contour validation.
- **`shapely>=2.0.0`**: Computational geometry library for calculating polygon area, perimeter, skeleton centerline, and localized aperture width.
- **`pydantic>=2.0.0`**: Schema validation and serialization for API contracts.
- **`anyio>=3.7.0`**: Async worker thread pool execution.

### Frontend Dependencies
- **React 18 + TypeScript + Vite**: Host client application.
- **Lucide React**: Engineering icons.
- **Tailwind CSS**: CAD technical drafting UI styling.
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Recommended Project Layout
```
backend/
├── app/
│   ├── main.py
│   ├── schemas.py              # Pydantic v2 API contracts
│   ├── services/
│   │   ├── crack_analyzer.py   # Primary analyzer orchestrator
│   │   ├── yolo_service.py     # Ultralytics YOLOv8 segmentation implementation
│   │   ├── morphometry.py      # Civil metrics: aperture, length, ACI classification
│   │   └── fallback_engine.py  # Deterministic fallback when weights unavailable
│   ├── utils/
│   │   └── telemetry.py        # Arize Phoenix / OpenTelemetry tracing setup
│   └── weights/
│       ├── .gitkeep
│       └── crack_yolov8s_seg.pt # Pretrained / benchmark crack weights
└── tests/
    ├── test_api.py
    ├── test_yolo_service.py
    └── test_morphometry.py
```

### Pattern 1: Asynchronous Worker Thread Offloading
```python
# FastAPI Route Pattern
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    contents = await file.read()
    # Offload synchronous PyTorch model inference to anyio thread pool
    result = await anyio.to_thread.run_sync(
        crack_analyzer.analyze, contents, file.filename
    )
    return result
```

### Pattern 2: Retina Masks with Polygon Normalization
```python
# YOLOv8 Extraction Pattern
results = model.predict(source=image, conf=0.25, iou=0.45, retina_masks=True, device=device, verbose=False)
result = results[0]

polygons = []
normalized_polygons = []

if result.masks is not None:
    for poly in result.masks.xy: # np.ndarray (N, 2) in pixel coordinates
        if len(poly) >= 3:
            poly_list = poly.tolist()
            polygons.append(poly_list)
            normalized_polygons.append([
                [round(x / width, 4), round(y / height, 4)] for x, y in poly_list
            ])
```

### Pattern 3: SVG Viewport Overlay in React
```tsx
// Frontend Canvas Rendering
<svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox={`0 0 ${imgWidth} ${imgHeight}`}>
  {polygons.map((poly, idx) => (
    <polygon
      key={idx}
      points={poly.map(pt => `${pt[0]},${pt[1]}`).join(' ')}
      className="fill-orange-500/30 stroke-orange-500 stroke-2 transition-all hover:fill-orange-500/50"
    />
  ))}
</svg>
```
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Contour polygon extraction | Manual OpenCV `findContours` on raw tensor masks | `result.masks.xy` from Ultralytics | Native C++ optimized vectorization already accounts for coordinate offsets and padding |
| Mask downsampling handling | Bilinear resizing of 160x160 masks | `retina_masks=True` in `.predict()` | Ultralytics calculates mask prototypes at full resolution before clipping |
| Geometry calculations | Custom polygon intersection math | `shapely.geometry.Polygon` | Handles self-intersecting loops, invalid geometries, and complex perimeter math |
| Device detection | Hardcoded `"cuda"` / `"cpu"` checks | `torch.backends.mps.is_available()` / device routing | Seamless cross-platform execution on macOS MPS and Linux CUDA |
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Event Loop Starvation
- **What goes wrong**: Calling `model.predict()` directly in `async def analyze_image()` blocks the Uvicorn event loop. Health checks (`/health`) and concurrent requests hang.
- **How to avoid**: Offload all inference calls using `anyio.to_thread.run_sync()`.

### Pitfall 2: Disappearing Hairline Cracks (Prototype Mask Downsampling)
- **What goes wrong**: YOLOv8 defaults to evaluating masks at 160x160 resolution, erasing thin 0.1–0.3 mm cracks.
- **How to avoid**: Always pass `retina_masks=True` in `model.predict()`.

### Pitfall 3: Crashing on Clean Images (`NoneType` Mask Access)
- **What goes wrong**: When zero cracks are detected, `result.masks` is `None` (not an empty array). `for mask in result.masks` throws `AttributeError: 'NoneType' object has no attribute 'xy'`.
- **How to avoid**: Guard check `if result.masks is not None and len(result.masks) > 0:`.

### Pitfall 4: Memory Bloat During High-Volume Inspection
- **What goes wrong**: Autograd calculation graphs build up in memory even when only predicting.
- **How to avoid**: Wrap inference blocks with `@torch.inference_mode()` or `with torch.inference_mode():`.
</common_pitfalls>

<code_examples>
## Code Examples

### Full Service Implementation Skeleton
```python
import io
import torch
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, Any, List, Optional
from ultralytics import YOLO

class YOLOv8SegmentationService:
    def __init__(self, weights_path: Optional[str] = None):
        self.device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
        default_weights = Path(__file__).parent.parent / "weights" / "crack_yolov8s_seg.pt"
        target_weights = weights_path or str(default_weights)
        
        if not Path(target_weights).exists():
            target_weights = "yolov8n-seg.pt"  # Automatically cached by Ultralytics
            
        self.model = YOLO(target_weights)
        self.model.to(self.device)

    @torch.inference_mode()
    def segment(self, file_bytes: bytes, conf: float = 0.25) -> Dict[str, Any]:
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        width, height = image.size

        results = self.model.predict(
            source=image,
            conf=conf,
            iou=0.45,
            retina_masks=True,
            device=self.device,
            verbose=False
        )
        
        result = results[0]
        polygons = []
        normalized_polygons = []
        boxes = []
        confidences = []

        if result.masks is not None and len(result.masks) > 0:
            for poly in result.masks.xy:
                if len(poly) >= 3:
                    p_list = poly.tolist()
                    polygons.append(p_list)
                    normalized_polygons.append([[round(x / width, 4), round(y / height, 4)] for x, y in p_list])
                    
            for box in result.boxes:
                boxes.append([round(float(v), 2) for v in box.xyxy[0].tolist()])
                confidences.append(round(float(box.conf[0]) * 100, 1))

        return {
            "has_crack": len(polygons) > 0,
            "defect_count": len(polygons),
            "polygons": polygons,
            "normalized_polygons": normalized_polygons,
            "bounding_boxes": boxes,
            "confidences": confidences,
            "dimensions": {"width": width, "height": height}
        }
```
</code_examples>

<validation_architecture>
## Validation Architecture

### Automated Verification Strategy
1. **Unit Tests (`test_yolo_service.py`)**:
   - Model instantiation with CPU and MPS support.
   - Inference with mock image bytes returning valid schema.
   - Empty image (zero defect) handling without `NoneType` error.
   - `retina_masks=True` verification.
2. **Integration Tests (`test_api.py`)**:
   - `POST /analyze` with benchmark image returning `polygons` and `has_segmentation: true`.
   - Backward compatibility: ensure existing frontend fields (`analysis_id`, `status`, `severity`, `confidence`) remain intact.
3. **Civil Metric Tests (`test_morphometry.py`)**:
   - Verification of aspect ratio filter (rejecting aspect ratio < 1.3:1 circular tie holes).
   - ACI 224R aperture category mapping.

### Test Execution Commands
- Quick test: `pytest backend/tests/test_api.py -v`
- Full suite: `pytest backend/tests/ -v --junitxml=test-reports/results.xml`
</validation_architecture>

<sources>
## Sources

### Primary (HIGH Confidence)
- Ultralytics YOLOv8 Documentation: https://docs.ultralytics.com/tasks/segment/
- PyTorch MPS Backend Documentation: https://pytorch.org/docs/stable/notes/mps.html
- FastAPI Asynchronous Concurrency Docs: https://fastapi.tiangolo.com/async/

### Secondary (HIGH Confidence)
- American Concrete Institute (ACI 224R-01): Control of Cracking in Concrete Structures
- Crack500 Open Benchmark Dataset: Public concrete surface fissure segmentation dataset
</sources>

---
*Phase: 03-yolov8-segmentation-pipeline-integration*
*Research completed: 2026-09-28*
*Ready for planning: yes*
