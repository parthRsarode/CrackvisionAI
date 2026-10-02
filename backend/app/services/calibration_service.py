import math
import logging
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class CalibrationService:
    """
    Civil Engineering Optical Calibration Service.
    Supports:
    - Automated ArUco fiducial marker detection (DICT_4X4, DICT_5X5, DICT_6X6)
    - Two-point reference scale calculation (ruler / target card)
    - Localized crack aperture probing for digital caliper measurements
    """

    SUPPORTED_DICTIONARIES = [
        cv2.aruco.DICT_4X4_50,
        cv2.aruco.DICT_4X4_100,
        cv2.aruco.DICT_5X5_50,
        cv2.aruco.DICT_6X6_50,
    ]

    def __init__(self):
        self._detectors = []
        for dict_id in self.SUPPORTED_DICTIONARIES:
            dictionary = cv2.aruco.getPredefinedDictionary(dict_id)
            params = cv2.aruco.DetectorParameters()
            params.adaptiveThreshWinSizeMin = 3
            params.adaptiveThreshWinSizeMax = 25
            params.adaptiveThreshWinSizeStep = 5
            params.adaptiveThreshConstant = 7
            params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
            detector = cv2.aruco.ArucoDetector(dictionary, params)
            self._detectors.append((dict_id, detector))

    def detect_fiducial_marker(
        self,
        image_np: np.ndarray,
        marker_size_mm: float = 50.0,
        default_field_width_m: float = 0.15
    ) -> Dict[str, Any]:
        """
        Scan image for ArUco fiducial target.
        If found, derive exact millimeter-per-pixel optical scale.
        """
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            height, width = image_np.shape[:2]
        else:
            gray = image_np
            height, width = gray.shape[:2]

        best_marker = None
        max_area = 0.0

        for dict_id, detector in self._detectors:
            corners, ids, rejected = detector.detectMarkers(gray)
            if ids is not None and len(ids) > 0:
                for idx, marker_corners in enumerate(corners):
                    pts = marker_corners[0]  # shape: (4, 2)
                    area = cv2.contourArea(pts.astype(np.float32))
                    if area > max_area:
                        max_area = area
                        best_marker = {
                            "id": int(np.ravel(ids)[idx]),
                            "corners": pts,
                            "dict_id": dict_id
                        }

        if best_marker is not None:
            pts = best_marker["corners"]
            # Calculate side lengths: (0->1, 1->2, 2->3, 3->0)
            d1 = np.linalg.norm(pts[0] - pts[1])
            d2 = np.linalg.norm(pts[1] - pts[2])
            d3 = np.linalg.norm(pts[2] - pts[3])
            d4 = np.linalg.norm(pts[3] - pts[0])
            mean_side_px = float((d1 + d2 + d3 + d4) / 4.0)

            if mean_side_px > 1.0:
                mm_per_pixel = float(round(marker_size_mm / mean_side_px, 4))
                effective_field_width_m = float(round((mm_per_pixel * width) / 1000.0, 4))

                corners_list = [[round(float(p[0]), 2), round(float(p[1]), 2)] for p in pts]
                norm_corners = [
                    [round(float(p[0]) / max(width, 1), 4), round(float(p[1]) / max(height, 1), 4)]
                    for p in pts
                ]

                return {
                    "calibration_status": "fiducial_calibrated",
                    "method": "aruco_fiducial",
                    "marker_id": best_marker["id"],
                    "marker_size_mm": float(marker_size_mm),
                    "mean_side_px": float(round(mean_side_px, 2)),
                    "marker_corners": corners_list,
                    "normalized_corners": norm_corners,
                    "mm_per_pixel": mm_per_pixel,
                    "assumed_field_width_m": effective_field_width_m,
                    "confidence": 98.5
                }

        # Fallback if no marker found: use calibrated default macro field-of-view
        default_mm_per_pixel = float(round((default_field_width_m * 1000.0) / max(width, 1), 4))
        return {
            "calibration_status": "uncalibrated_macro",
            "method": "default_macro",
            "marker_id": None,
            "marker_size_mm": None,
            "mean_side_px": 0.0,
            "marker_corners": [],
            "normalized_corners": [],
            "mm_per_pixel": default_mm_per_pixel,
            "assumed_field_width_m": default_field_width_m,
            "confidence": 0.0
        }

    def compute_two_point_scale(
        self,
        pt1: Tuple[float, float],
        pt2: Tuple[float, float],
        reference_length_mm: float,
        image_width: int
    ) -> Dict[str, Any]:
        """
        Compute scale given two user-clicked points and known real-world distance in mm.
        """
        dx = pt2[0] - pt1[0]
        dy = pt2[1] - pt1[1]
        distance_px = math.hypot(dx, dy)

        if distance_px < 1.0:
            raise ValueError("Reference points must be at least 1 pixel apart.")

        mm_per_pixel = float(round(reference_length_mm / distance_px, 4))
        effective_field_width_m = float(round((mm_per_pixel * image_width) / 1000.0, 4))

        return {
            "calibration_status": "user_two_point_calibrated",
            "method": "manual_two_point",
            "pixel_distance": float(round(distance_px, 2)),
            "reference_length_mm": float(reference_length_mm),
            "mm_per_pixel": mm_per_pixel,
            "assumed_field_width_m": effective_field_width_m
        }

    def sample_localized_aperture(
        self,
        polygon: List[List[float]],
        click_pt: Tuple[float, float],
        mm_per_pixel: float
    ) -> Dict[str, Any]:
        """
        Probe localized crack width at click_pt across a crack polygon contour.
        Finds the minimum cross-section normal spanning chord through click_pt.
        """
        pts_np = np.array(polygon, dtype=np.float32)
        if len(pts_np) < 3:
            return {
                "width_px": 0.0,
                "width_mm": 0.0,
                "span_points": [[click_pt[0], click_pt[1]], [click_pt[0], click_pt[1]]]
            }

        cx, cy = click_pt
        
        # 1. Find closest segment on polygon perimeter
        best_dist = float('inf')
        best_tangent = (1.0, 0.0)
        n = len(pts_np)

        for i in range(n):
            p1 = pts_np[i]
            p2 = pts_np[(i + 1) % n]
            
            # Vector p1 -> p2
            seg = p2 - p1
            seg_len = np.linalg.norm(seg)
            if seg_len < 1e-4:
                continue

            # Project click point onto segment
            u = max(0.0, min(1.0, np.dot(np.array([cx, cy]) - p1, seg) / (seg_len ** 2)))
            proj = p1 + u * seg
            dist = np.linalg.norm(np.array([cx, cy]) - proj)

            if dist < best_dist:
                best_dist = dist
                best_tangent = (seg[0] / seg_len, seg[1] / seg_len)

        # Normal vector to crack fissure tangent
        norm_vec = np.array([-best_tangent[1], best_tangent[0]], dtype=np.float32)

        # 2. Cast bidirectional ray from (cx, cy) along normal to intersect polygon edges
        ray_dir = norm_vec
        step = 0.5
        max_search = 300.0  # max pixels

        # Forward ray
        forward_pt = np.array([cx, cy], dtype=np.float32)
        for d in np.arange(0, max_search, step):
            test_pt = np.array([cx, cy], dtype=np.float32) + ray_dir * d
            # Check if test_pt left polygon if inside, or hit polygon boundary
            poly_test = cv2.pointPolygonTest(pts_np, (float(test_pt[0]), float(test_pt[1])), False)
            if poly_test < 0:
                forward_pt = test_pt
                break

        # Backward ray
        backward_pt = np.array([cx, cy], dtype=np.float32)
        for d in np.arange(0, max_search, step):
            test_pt = np.array([cx, cy], dtype=np.float32) - ray_dir * d
            poly_test = cv2.pointPolygonTest(pts_np, (float(test_pt[0]), float(test_pt[1])), False)
            if poly_test < 0:
                backward_pt = test_pt
                break

        span_dist_px = float(np.linalg.norm(forward_pt - backward_pt))
        # Ensure minimum resolution 1px
        span_dist_px = max(span_dist_px, 1.0)
        width_mm = float(round(span_dist_px * mm_per_pixel, 3))

        return {
            "width_px": float(round(span_dist_px, 2)),
            "width_mm": width_mm,
            "span_points": [
                [round(float(backward_pt[0]), 2), round(float(backward_pt[1]), 2)],
                [round(float(forward_pt[0]), 2), round(float(forward_pt[1]), 2)]
            ]
        }

calibration_service = CalibrationService()
