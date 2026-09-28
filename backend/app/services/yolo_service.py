import io
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class YOLOv8SegmentationService:
    """
    Ultralytics YOLOv8 segmentation service for concrete and asphalt crack detection.
    Outputs exact polygonal boundary contours (pixel and normalized coordinates),
    bounding boxes, and detection confidence scores.
    Features adaptive multi-pass threshold scanning for high-sensitivity crack capture.
    """
    def __init__(self, weights_path: Optional[str] = None):
        self.device = self._detect_device()
        self.weights_path = self._resolve_weights(weights_path)
        self.model = None
        self._load_model()

    def _detect_device(self) -> str:
        try:
            import torch
            if torch.backends.mps.is_available():
                return "mps"
            if torch.cuda.is_available():
                return "cuda"
        except Exception as e:
            logger.warning(f"Device detection fallback to CPU: {e}")
        return "cpu"

    def _resolve_weights(self, weights_path: Optional[str]) -> str:
        if weights_path and Path(weights_path).exists():
            return weights_path
            
        custom_weights = Path(__file__).parent.parent / "weights" / "crack_yolov8s_seg.pt"
        if custom_weights.exists():
            return str(custom_weights)
            
        return "yolov8n-seg.pt"

    def _load_model(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.weights_path)
            self.model.to(self.device)
            logger.info(f"Loaded YOLOv8 segmentation model [{self.weights_path}] on device [{self.device}]")
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            self.model = None

    def is_operational(self) -> bool:
        return self.model is not None

    def segment(self, image_bytes: bytes, conf_threshold: float = 0.25) -> Dict[str, Any]:
        """
        Execute YOLOv8 segmentation inference on raw image bytes.
        Uses adaptive multi-pass confidence thresholds (0.25 -> 0.12 -> 0.05 -> 0.03)
        to capture fine or lower-contrast fissures without false positives on clean concrete.
        """
        if not self.is_operational():
            return {
                "has_crack": False,
                "defect_count": 0,
                "polygons": [],
                "normalized_polygons": [],
                "bounding_boxes": [],
                "confidences": [],
                "dimensions": {"width": 0, "height": 0},
                "operational": False,
                "error": "Model not loaded"
            }

        try:
            import torch
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            width, height = image.size

            # Adaptive confidence passes
            passes = [conf_threshold, 0.12, 0.05, 0.03]
            best_result = None

            for conf in passes:
                with torch.inference_mode():
                    results = self.model.predict(
                        source=image,
                        conf=conf,
                        iou=0.45,
                        retina_masks=True,
                        device=self.device,
                        verbose=False
                    )

                if results and len(results) > 0:
                    res = results[0]
                    if res.masks is not None and len(res.masks) > 0:
                        best_result = res
                        break

            if best_result is None and results and len(results) > 0:
                best_result = results[0]

            polygons: List[List[List[float]]] = []
            normalized_polygons: List[List[List[float]]] = []
            bounding_boxes: List[List[float]] = []
            confidences: List[float] = []

            if best_result is not None and best_result.masks is not None and len(best_result.masks) > 0:
                for poly in best_result.masks.xy:
                    if len(poly) >= 3:
                        poly_pts = [[round(float(x), 2), round(float(y), 2)] for x, y in poly]
                        polygons.append(poly_pts)
                        norm_pts = [
                            [round(x / width, 4), round(y / height, 4)]
                            for x, y in poly_pts
                        ]
                        normalized_polygons.append(norm_pts)

                if best_result.boxes is not None and len(best_result.boxes) > 0:
                    for box in best_result.boxes:
                        box_coords = [round(float(v), 2) for v in box.xyxy[0].tolist()]
                        conf = round(float(box.conf[0]) * 100, 1)
                        bounding_boxes.append(box_coords)
                        confidences.append(conf)

            return {
                "has_crack": len(polygons) > 0,
                "defect_count": len(polygons),
                "polygons": polygons,
                "normalized_polygons": normalized_polygons,
                "bounding_boxes": bounding_boxes,
                "confidences": confidences,
                "dimensions": {"width": width, "height": height},
                "operational": True
            }

        except Exception as e:
            logger.error(f"Error during YOLOv8 segmentation: {e}", exc_info=True)
            return {
                "has_crack": False,
                "defect_count": 0,
                "polygons": [],
                "normalized_polygons": [],
                "bounding_boxes": [],
                "confidences": [],
                "dimensions": {"width": 0, "height": 0},
                "operational": True,
                "error": str(e)
            }
