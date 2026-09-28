import math
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

class MorphometryService:
    """
    Civil engineering morphometry analysis for detected crack fissures.
    Implements:
    - Non-defect artifact filtering (tie-hole and shadow rejection)
    - Structural crack orientation classification (shear, shrinkage, settlement)
    - ACI 224R-01 permissible limit compliance evaluation
    - ASTM C881 remediation recommendation selection
    """

    ACI_224R_LIMITS = {
        "water_retaining": 0.10,      # mm (0.004 in.)
        "deicing_marine": 0.15,       # mm (0.006 in.)
        "humidity_soil": 0.30,        # mm (0.012 in.)
        "dry_air_protected": 0.41      # mm (0.016 in.)
    }

    def filter_artifacts(
        self,
        polygons: List[List[List[float]]],
        boxes: List[List[float]],
        confidences: List[float]
    ) -> Tuple[List[List[List[float]]], List[List[float]], List[float]]:
        """
        Filter out non-crack artifacts such as circular tie-holes and broad shadow patches.
        A linear crack fissure has a high aspect ratio (elongated).
        Circular tie holes typically have aspect ratios near 1.0 (e.g. < 1.3:1) and large solid area.
        """
        filtered_polys = []
        filtered_boxes = []
        filtered_confs = []

        for poly, box, conf in zip(polygons, boxes, confidences):
            x1, y1, x2, y2 = box
            w = max(abs(x2 - x1), 1.0)
            h = max(abs(y2 - y1), 1.0)
            
            # Aspect ratio is length of long side / short side
            aspect_ratio = max(w, h) / min(w, h)
            area = w * h

            # Reject circular / blob artifacts with low elongation and significant area
            if aspect_ratio < 1.3 and area > 1000:
                continue  # Discard tie-hole or blob artifact

            filtered_polys.append(poly)
            filtered_boxes.append(box)
            filtered_confs.append(conf)

        return filtered_polys, filtered_boxes, filtered_confs

    def classify_orientation(self, box: List[float]) -> str:
        """
        Determine crack classification based on geometric orientation.
        0°-30° relative to horizontal: Horizontal settlement crack
        30°-60°: Diagonal shear crack (structural distress)
        60°-90°: Vertical shrinkage crack
        """
        x1, y1, x2, y2 = box
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        angle_deg = math.degrees(math.atan2(dy, max(dx, 1e-4)))

        if angle_deg < 30:
            return "Horizontal settlement crack"
        elif angle_deg < 60:
            return "Diagonal shear crack"
        else:
            return "Vertical shrinkage crack"

    def estimate_aperture_and_severity(
        self,
        polygons: List[List[List[float]]],
        image_width: int,
        image_height: int,
        assumed_field_width_m: float = 1.0
    ) -> Dict[str, Any]:
        """
        Estimate crack width (aperture) in millimeters based on polygon profile
        and optical scaling (defaulting to 1.0m field of view if uncalibrated).
        """
        if not polygons:
            return {
                "severity": "low",
                "estimated_width": "0.0 mm",
                "max_aperture_mm": 0.0,
                "affected_area": "0.0%",
                "recommendation": "Routine inspection recommended. No active crack distress identified.",
                "aci_compliance": {
                    "water_retaining": True,
                    "deicing_marine": True,
                    "humidity_soil": True,
                    "dry_air_protected": True
                }
            }

        # Millimeters per pixel calibration scale
        mm_per_pixel = (assumed_field_width_m * 1000.0) / max(image_width, 1)

        # Estimate average and maximum fissure thickness
        total_poly_area = 0.0
        max_width_px = 0.0

        for poly in polygons:
            pts = np.array(poly)
            if len(pts) >= 3:
                # Green's theorem polygon area
                x = pts[:, 0]
                y = pts[:, 1]
                area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
                total_poly_area += area
                
                # Perimeter
                diffs = np.diff(pts, axis=0, append=[pts[0]])
                perimeter = np.sum(np.hypot(diffs[:, 0], diffs[:, 1]))
                
                # Approximate hydraulic diameter / thickness = 2 * Area / Perimeter
                if perimeter > 0:
                    thickness_px = (2.0 * area) / perimeter
                    max_width_px = max(max_width_px, thickness_px)

        # Scale to millimeters
        estimated_aperture_mm = round(max(max_width_px * mm_per_pixel, 0.15), 2)
        min_aperture_mm = round(max(estimated_aperture_mm * 0.6, 0.10), 2)
        
        # Calculate percentage of surface affected
        img_area = max(image_width * image_height, 1)
        area_pct = round((total_poly_area / img_area) * 100.0, 1)
        area_pct_str = f"{max(area_pct, 0.1)}%"

        # Categorize severity based on ACI 224R thresholds
        if estimated_aperture_mm <= 0.30:
            severity = "low"
            recommendation = (
                "Monitor crack development during scheduled inspections. "
                "Apply low-viscosity penetrant or surface seal (ASTM C881 Type I, Grade 1) if moisture egress occurs."
            )
        elif estimated_aperture_mm <= 1.00:
            severity = "medium"
            recommendation = (
                "Schedule detailed forensic inspection. Clean fissure and execute structural pressure injection "
                "with epoxy resin complying with ASTM C881 Type IV, Grade 1."
            )
        else:
            severity = "high"
            recommendation = (
                "CRITICAL: Immediate structural evaluation by Licensed Professional Engineer (PE/SE) required. "
                "Active structural movement or shear distress suspected; prepare shoring or load restriction."
            )

        # Evaluate ACI compliance
        compliance = {
            "water_retaining": bool(estimated_aperture_mm <= self.ACI_224R_LIMITS["water_retaining"]),
            "deicing_marine": bool(estimated_aperture_mm <= self.ACI_224R_LIMITS["deicing_marine"]),
            "humidity_soil": bool(estimated_aperture_mm <= self.ACI_224R_LIMITS["humidity_soil"]),
            "dry_air_protected": bool(estimated_aperture_mm <= self.ACI_224R_LIMITS["dry_air_protected"])
        }

        return {
            "severity": str(severity),
            "estimated_width": f"{min_aperture_mm} - {estimated_aperture_mm} mm",
            "max_aperture_mm": float(estimated_aperture_mm),
            "affected_area": str(area_pct_str),
            "recommendation": str(recommendation),
            "aci_compliance": compliance
        }
