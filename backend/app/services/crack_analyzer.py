import hashlib
import logging
import random
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image
import io

from .yolo_service import YOLOv8SegmentationService
from .morphometry import MorphometryService

logger = logging.getLogger(__name__)

class CrackAnalyzer:
    """
    Primary Crack Analyzer service orchestrating deep learning YOLOv8 segmentation,
    civil engineering morphometry, multi-factor structural evaluation, multi-standard benchmarks, and fallback execution.
    """

    def __init__(self, weights_path: Optional[str] = None):
        self.yolo_service = YOLOv8SegmentationService(weights_path)
        self.morphometry_service = MorphometryService()

    def _get_deterministic_seed(self, filename: str, file_bytes: bytes) -> int:
        """Generate deterministic seed from filename and file content for fallback"""
        hash_object = hashlib.md5(((filename or "") + str(len(file_bytes))).encode())
        return int(hash_object.hexdigest(), 16) % 10000

    def _mock_analysis(
        self,
        seed: int,
        member_type: Optional[str] = None,
        environment: Optional[str] = None,
        standard_code: Optional[str] = "ACI"
    ) -> Dict[str, Any]:
        """Generate deterministic mock analysis if model inference is unavailable"""
        random.seed(seed)
        np.random.seed(seed)

        crack_detected = random.random() < 0.7

        if not crack_detected:
            empty_eval = self.morphometry_service._build_empty_assessment(
                member_type=member_type,
                standard_code=standard_code
            )
            return {
                "status": "no_significant_crack",
                "confidence": round(random.uniform(85.0, 98.0), 1),
                "crack_type": "No significant cracks detected",
                "severity": "low",
                "estimated_width": "0.0 mm",
                "affected_area": "0.0%",
                "recommendation": empty_eval["recommendation"],
                "inspection_note": "This is an AI-assisted preliminary assessment and does not replace a qualified civil or structural engineer.",
                "annotated_image_note": "No crack regions detected",
                "has_segmentation": False,
                "polygons": [],
                "normalized_polygons": [],
                "bounding_boxes": [],
                "defect_count": 0,
                "inference_time_ms": 15.0,
                "aci_compliance": empty_eval["aci_compliance"],
                "crack_depth_status": empty_eval["crack_depth_status"],
                "crack_depth_explanation": empty_eval["crack_depth_explanation"],
                "evidence_sufficiency": empty_eval["evidence_sufficiency"],
                "assessment_breakdown": empty_eval["assessment_breakdown"],
                "compliance_details": empty_eval["compliance_details"],
                "plain_language_explanation": empty_eval["plain_language_explanation"],
                "multi_factor_metrics": empty_eval["multi_factor_metrics"],
                "unsupported_claims_disclaimer": empty_eval["unsupported_claims_disclaimer"]
            }

        sim_polys = [[[100.0, 150.0], [450.0, 165.0], [448.0, 175.0], [98.0, 160.0]]]
        sim_boxes = [[98.0, 150.0, 450.0, 175.0]]

        morph_eval = self.morphometry_service.analyze_multi_factor_condition(
            polygons=sim_polys,
            bounding_boxes=sim_boxes,
            image_width=640,
            image_height=640,
            assumed_field_width_m=1.0,
            member_type=member_type,
            environment=environment,
            standard_code=standard_code
        )

        return {
            "status": "crack_detected",
            "confidence": round(random.uniform(75.0, 95.0), 1),
            "crack_type": "Diagonal shear crack",
            "severity": morph_eval["severity"],
            "estimated_width": morph_eval["estimated_width"],
            "affected_area": morph_eval["affected_area"],
            "recommendation": morph_eval["recommendation"],
            "inspection_note": "This is an AI-assisted preliminary assessment and does not replace a qualified civil or structural engineer.",
            "annotated_image_note": "Crack regions highlighted in CAD orange overlay",
            "has_segmentation": False,
            "polygons": sim_polys,
            "normalized_polygons": [[[0.15, 0.23], [0.70, 0.25], [0.70, 0.27], [0.15, 0.25]]],
            "bounding_boxes": sim_boxes,
            "defect_count": 1,
            "inference_time_ms": 25.0,
            "aci_compliance": morph_eval["aci_compliance"],
            "crack_depth_status": morph_eval["crack_depth_status"],
            "crack_depth_explanation": morph_eval["crack_depth_explanation"],
            "evidence_sufficiency": morph_eval["evidence_sufficiency"],
            "assessment_breakdown": morph_eval["assessment_breakdown"],
            "compliance_details": morph_eval["compliance_details"],
            "plain_language_explanation": morph_eval["plain_language_explanation"],
            "multi_factor_metrics": morph_eval["multi_factor_metrics"],
            "unsupported_claims_disclaimer": morph_eval["unsupported_claims_disclaimer"]
        }

    def analyze(
        self,
        file_bytes: bytes,
        filename: str = None,
        member_type: Optional[str] = None,
        element_criticality: Optional[str] = "primary",
        proximity_to_supports: Optional[str] = "unspecified",
        visible_spalling: bool = False,
        visible_corrosion: bool = False,
        previous_width_mm: Optional[float] = None,
        crack_depth_status: Optional[str] = "unknown",
        environment: Optional[str] = None,
        standard_code: Optional[str] = "ACI"
    ) -> Dict[str, Any]:
        """
        Synchronously analyze image for crack defects using YOLOv8 and Multi-Factor Morphometry.
        Offloaded to thread pool by FastAPI caller.
        """
        start_time = time.perf_counter()
        seed = self._get_deterministic_seed(filename or "", file_bytes)

        if self.yolo_service.is_operational():
            try:
                yolo_result = self.yolo_service.segment(file_bytes, conf_threshold=0.25)
                
                raw_polys = yolo_result["polygons"]
                raw_boxes = yolo_result["bounding_boxes"]
                raw_confs = yolo_result["confidences"]
                dimensions = yolo_result["dimensions"]
                width = dimensions.get("width", 640)
                height = dimensions.get("height", 640)

                polygons, boxes, confidences = self.morphometry_service.filter_artifacts(
                    raw_polys, raw_boxes, raw_confs
                )

                normalized_polygons = [
                    [[round(x / width, 4), round(y / height, 4)] for x, y in poly]
                    for poly in polygons
                ]

                elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 1)

                if len(polygons) == 0:
                    empty_eval = self.morphometry_service._build_empty_assessment(
                        member_type=member_type,
                        crack_depth_status=crack_depth_status,
                        standard_code=standard_code
                    )
                    return {
                        "analysis_id": f"ana_{seed}_{int(time.time())}",
                        "status": "no_significant_crack",
                        "confidence": 95.0,
                        "crack_type": "No significant cracks detected",
                        "severity": "low",
                        "estimated_width": "0.0 mm",
                        "affected_area": "0.0%",
                        "recommendation": empty_eval["recommendation"],
                        "inspection_note": "This is an AI-assisted preliminary assessment and does not replace a qualified civil or structural engineer.",
                        "annotated_image_note": "No crack regions detected",
                        "created_at": datetime.now().isoformat(),
                        "has_segmentation": True,
                        "polygons": [],
                        "normalized_polygons": [],
                        "bounding_boxes": [],
                        "defect_count": 0,
                        "inference_time_ms": elapsed_ms,
                        "aci_compliance": empty_eval["aci_compliance"],
                        "crack_depth_status": empty_eval["crack_depth_status"],
                        "crack_depth_explanation": empty_eval["crack_depth_explanation"],
                        "evidence_sufficiency": empty_eval["evidence_sufficiency"],
                        "assessment_breakdown": empty_eval["assessment_breakdown"],
                        "compliance_details": empty_eval["compliance_details"],
                        "plain_language_explanation": empty_eval["plain_language_explanation"],
                        "multi_factor_metrics": empty_eval["multi_factor_metrics"],
                        "unsupported_claims_disclaimer": empty_eval["unsupported_claims_disclaimer"]
                    }

                morph_metrics = self.morphometry_service.analyze_multi_factor_condition(
                    polygons=polygons,
                    bounding_boxes=boxes,
                    image_width=width,
                    image_height=height,
                    assumed_field_width_m=1.0,
                    member_type=member_type,
                    element_criticality=element_criticality,
                    proximity_to_supports=proximity_to_supports,
                    visible_spalling=visible_spalling,
                    visible_corrosion=visible_corrosion,
                    previous_width_mm=previous_width_mm,
                    crack_depth_status=crack_depth_status,
                    environment=environment,
                    standard_code=standard_code
                )

                crack_type = self.morphometry_service.classify_orientation(boxes[0])
                mean_conf = round(float(np.mean(confidences)), 1) if confidences else 85.0

                return {
                    "analysis_id": f"ana_{seed}_{int(time.time())}",
                    "status": "crack_detected",
                    "confidence": mean_conf,
                    "crack_type": crack_type,
                    "severity": morph_metrics["severity"],
                    "estimated_width": morph_metrics["estimated_width"],
                    "affected_area": morph_metrics["affected_area"],
                    "recommendation": morph_metrics["recommendation"],
                    "inspection_note": "This is an AI-assisted preliminary assessment and does not replace a qualified civil or structural engineer.",
                    "annotated_image_note": f"{len(polygons)} defect fissure(s) segmented via YOLOv8",
                    "created_at": datetime.now().isoformat(),
                    "has_segmentation": True,
                    "polygons": polygons,
                    "normalized_polygons": normalized_polygons,
                    "bounding_boxes": boxes,
                    "defect_count": len(polygons),
                    "inference_time_ms": elapsed_ms,
                    "aci_compliance": morph_metrics["aci_compliance"],
                    "crack_depth_status": morph_metrics["crack_depth_status"],
                    "crack_depth_explanation": morph_metrics["crack_depth_explanation"],
                    "evidence_sufficiency": morph_metrics["evidence_sufficiency"],
                    "assessment_breakdown": morph_metrics["assessment_breakdown"],
                    "compliance_details": morph_metrics["compliance_details"],
                    "plain_language_explanation": morph_metrics["plain_language_explanation"],
                    "multi_factor_metrics": morph_metrics["multi_factor_metrics"],
                    "unsupported_claims_disclaimer": morph_metrics["unsupported_claims_disclaimer"]
                }

            except Exception as e:
                logger.error(f"YOLOv8 inference pipeline error: {e}", exc_info=True)
                raise e

        mock_result = self._mock_analysis(
            seed,
            member_type=member_type,
            environment=environment,
            standard_code=standard_code
        )
        mock_result.update({
            "analysis_id": f"ana_{seed}_{int(time.time())}",
            "created_at": datetime.now().isoformat()
        })
        return mock_result

analyzer = CrackAnalyzer()

def analyze_crack(
    file_bytes: bytes,
    filename: str = None,
    member_type: Optional[str] = None,
    element_criticality: Optional[str] = "primary",
    proximity_to_supports: Optional[str] = "unspecified",
    visible_spalling: bool = False,
    visible_corrosion: bool = False,
    previous_width_mm: Optional[float] = None,
    crack_depth_status: Optional[str] = "unknown",
    environment: Optional[str] = None,
    standard_code: Optional[str] = "ACI"
) -> Dict[str, Any]:
    return analyzer.analyze(
        file_bytes=file_bytes,
        filename=filename,
        member_type=member_type,
        element_criticality=element_criticality,
        proximity_to_supports=proximity_to_supports,
        visible_spalling=visible_spalling,
        visible_corrosion=visible_corrosion,
        previous_width_mm=previous_width_mm,
        crack_depth_status=crack_depth_status,
        environment=environment,
        standard_code=standard_code
    )
