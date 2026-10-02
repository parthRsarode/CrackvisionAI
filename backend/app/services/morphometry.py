import math
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

class MorphometryService:
    """
    Civil engineering morphometry and structural condition assessment service.
    Implements multi-factor evaluation across:
    - Crack geometry (width, length, area, density, pattern, count, spacing)
    - Structural member context (type, primary vs secondary, proximity to supports)
    - Visible distress indicators (spalling, exposed rebar, corrosion staining)
    - Multi-code standards integration (ACI CODE-562/224R, Eurocode 2, IS 456:2000, BS 8110)
    - Evidence sufficiency auditing & explicit depth limitations
    """

    STANDARDS_LIMITS = {
        "ACI": {
            "name": "ACI CODE-562-21 & ACI 224R-01 (USA)",
            "water_retaining": 0.10,
            "deicing_marine": 0.15,
            "humidity_soil": 0.30,
            "dry_air_protected": 0.41
        },
        "EUROCODE_2": {
            "name": "Eurocode 2 (EN 1992-1-1 / EN 1992-3, Europe)",
            "water_retaining": 0.10,
            "deicing_marine": 0.20,
            "humidity_soil": 0.30,
            "dry_air_protected": 0.40
        },
        "IS_456": {
            "name": "IS 456:2000 Code of Practice (India)",
            "water_retaining": 0.10,
            "deicing_marine": 0.20,
            "humidity_soil": 0.20,
            "dry_air_protected": 0.30
        },
        "BS_8110": {
            "name": "BS 8110 / BS 8500 (United Kingdom)",
            "water_retaining": 0.10,
            "deicing_marine": 0.20,
            "humidity_soil": 0.30,
            "dry_air_protected": 0.30
        }
    }

    ACI_224R_LIMITS = STANDARDS_LIMITS["ACI"]

    def filter_artifacts(
        self,
        polygons: List[List[List[float]]],
        boxes: List[List[float]],
        confidences: List[float]
    ) -> Tuple[List[List[List[float]]], List[List[float]], List[float]]:
        import cv2
        import numpy as np
        
        filtered_polys = []
        filtered_boxes = []
        filtered_confs = []

        for poly, box, conf in zip(polygons, boxes, confidences):
            x1, y1, x2, y2 = box
            w = max(abs(x2 - x1), 1.0)
            h = max(abs(y2 - y1), 1.0)
            aspect_ratio = max(w, h) / min(w, h)
            area = w * h

            # Reject circular / blob artifacts with low elongation and significant area (e.g. tie-holes)
            if aspect_ratio < 1.3 and area > 1000:
                continue

            poly_np = np.array(poly, dtype=np.float32)
            poly_area = cv2.contourArea(poly_np)
            box_area = max((x2 - x1) * (y2 - y1), 1.0)
            extent = poly_area / box_area
            
            # Filter out solid rectangular blocks (like text background blocks or stamps)
            # which have low elongation (aspect_ratio < 2.5) and high solidity (extent > 0.50).
            if aspect_ratio < 2.5 and extent > 0.50 and area > 500:
                continue
            
            filtered_polys.append([[float(x), float(y)] for x, y in poly])
            filtered_boxes.append([float(x1), float(y1), float(x2), float(y2)])
            filtered_confs.append(float(conf))

        return filtered_polys, filtered_boxes, filtered_confs

    def classify_orientation(self, box: List[float]) -> str:
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
        Backwards-compatible wrapper around analyze_multi_factor_condition.
        """
        return self.analyze_multi_factor_condition(
            polygons=polygons,
            bounding_boxes=[],
            image_width=image_width,
            image_height=image_height,
            assumed_field_width_m=assumed_field_width_m,
            standard_code="ACI"
        )

    def analyze_multi_factor_condition(
        self,
        polygons: List[List[List[float]]],
        bounding_boxes: List[List[float]],
        image_width: int,
        image_height: int,
        assumed_field_width_m: float = 0.15,
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
        selected_standard_key = (standard_code or "ACI").upper()
        if selected_standard_key not in self.STANDARDS_LIMITS:
            selected_standard_key = "ACI"
        standard_info = self.STANDARDS_LIMITS[selected_standard_key]

        # Calibrated Optical Scale (Defaulting to 0.15m macro inspection FOV)
        mm_per_pixel = (assumed_field_width_m * 1000.0) / max(image_width, 1)

        if not polygons:
            return self._build_empty_assessment(
                member_type=member_type,
                crack_depth_status=crack_depth_status,
                standard_code=selected_standard_key
            )

        # 1. Morphometric calculations (Width, Length, Area, Density, Pattern)
        total_poly_area_px = 0.0
        total_perimeter_px = 0.0
        max_thickness_px = 0.0
        total_length_px = 0.0

        for poly in polygons:
            pts = np.array(poly)
            if len(pts) >= 3:
                x = pts[:, 0]
                y = pts[:, 1]
                area = float(0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))
                total_poly_area_px += area

                diffs = np.diff(pts, axis=0, append=[pts[0]])
                perimeter = float(np.sum(np.hypot(diffs[:, 0], diffs[:, 1])))
                total_perimeter_px += perimeter
                total_length_px += perimeter / 2.0

                if perimeter > 0:
                    thickness_px = (2.0 * area) / perimeter
                    max_thickness_px = max(max_thickness_px, thickness_px)

        estimated_aperture_mm = float(round(max(max_thickness_px * mm_per_pixel, 0.15), 2))
        min_aperture_mm = float(round(max(estimated_aperture_mm * 0.6, 0.10), 2))
        total_length_mm = float(round(total_length_px * mm_per_pixel, 1))
        total_area_mm2 = float(round(total_poly_area_px * (mm_per_pixel ** 2), 1))

        img_area_px = max(image_width * image_height, 1)
        area_pct = float(round((total_poly_area_px / img_area_px) * 100.0, 2))
        area_pct_str = f"{max(area_pct, 0.1)}%"

        crack_count = int(len(polygons))
        pattern = "Branching / Network" if crack_count > 1 else "Single Continuous Linear Fissure"

        # 2. Crack Depth / Internal Condition Handling
        depth_status = str(crack_depth_status or "unknown")
        depth_explanation = (
            f"Measured surface crack width: {estimated_aperture_mm} mm. "
            "Crack depth cannot be established from surface optical images alone. "
            "Structural significance therefore cannot be determined from surface aperture width alone."
        )

        # 3. Evidence Sufficiency Evaluation
        missing_factors = []
        if depth_status in ["unknown", "not_assessed", "surface_only"]:
            missing_factors.append("internal_crack_depth_scan")
        if not member_type or member_type == "custom":
            missing_factors.append("verified_structural_member_type")
        if previous_width_mm is None:
            missing_factors.append("historical_progression_baseline")

        if len(missing_factors) >= 1:
            evidence_sufficiency = {
                "status": "insufficient_for_engineering_assessment",
                "missing_factors": missing_factors,
                "summary": "Surface evidence captured cleanly, but full structural engineering interpretation requires additional contextual or NDT inspection data."
            }
        else:
            evidence_sufficiency = {
                "status": "sufficient_for_surface_assessment",
                "missing_factors": [],
                "summary": "Sufficient surface and contextual evidence present for preliminary engineering surface evaluation."
            }

        # 4. Multi-Factor Severity Logic
        severity_points = 0
        
        if estimated_aperture_mm >= 0.75:
            severity_points += 3
        elif estimated_aperture_mm >= 0.30:
            severity_points += 2
        else:
            severity_points += 1

        is_primary = (element_criticality == "primary")
        near_support = (proximity_to_supports in ["near_support", "connection"])
        if is_primary and near_support:
            severity_points += 2
        elif is_primary or near_support:
            severity_points += 1

        if visible_spalling:
            severity_points += 2
        if visible_corrosion:
            severity_points += 2

        is_expanding = False
        if previous_width_mm is not None and estimated_aperture_mm > (previous_width_mm + 0.1):
            severity_points += 2
            is_expanding = True

        if severity_points >= 6:
            severity = "high"
            recommendation = (
                "IMMEDIATE ACTION RECOMMENDED: Detailed forensic evaluation by Licensed Professional Engineer (PE/SE). "
                "The combination of surface width, structural location, visible deterioration indicators, or active progression warrants "
                "physical NDT (Ultrasonic Pulse Velocity or Core Sampling) and structural shoring review."
            )
        elif severity_points >= 3:
            severity = "medium"
            recommendation = (
                "MONITOR & SEAL: Schedule forensic inspection. Clean crack fissure and apply surface sealant or epoxy pressure injection "
                "complying with ASTM C881 Type IV Grade 1. Establish benchmark displacement gauges to track ongoing crack progression."
            )
        else:
            severity = "low"
            recommendation = (
                "ROUTINE MONITORING: Monitor crack development during periodic structural maintenance inspections. "
                "Apply low-viscosity surface penetrant or sealer if moisture egress or freeze-thaw exposure occurs."
            )

        # 5. Assessment Breakdown
        location_desc = proximity_to_supports.replace('_', ' ').capitalize() if proximity_to_supports else "Unspecified location"
        member_desc = str(member_type or "Structural Concrete Surface")
        
        progression_note = (
            f"Active width expansion recorded (previously {previous_width_mm} mm)."
            if is_expanding
            else ("Historical baseline unavailable." if previous_width_mm is None else f"Consistent with historical measurement ({previous_width_mm} mm).")
        )

        assessment_breakdown = {
            "observation": f"Maximum surface aperture: {estimated_aperture_mm} mm. Estimated length: {total_length_mm} mm ({crack_count} fissure(s), {pattern}).",
            "context": f"Element: {member_desc} ({'Primary Load-Bearing' if is_primary else 'Secondary Element'}). Location: {location_desc}.",
            "deterioration": f"Visible Spalling: {'Yes' if visible_spalling else 'None detected'}. Corrosion Stain: {'Yes' if visible_corrosion else 'None detected'}. Progression: {progression_note}.",
            "assessment": (
                f"Condition category assigned based on multi-factor synthesis (Geometry score + Context + Deterioration indicators). "
                f"The crack is located on a {member_desc.lower()} and displays {pattern.lower()}. "
                f"Evaluated against standard: {standard_info['name']}. Because internal depth is unverified, this result represents a surface condition evaluation."
            )
        }

        # 6. Multi-Code Compliance
        env_lower = (environment or "").lower()
        if "marine" in env_lower or "salt" in env_lower or "severe" in env_lower:
            permissible_limit_mm = float(standard_info["deicing_marine"])
            env_name = "Deicing Chemicals & Seawater Spray"
        elif "humid" in env_lower or "soil" in env_lower or "moist" in env_lower:
            permissible_limit_mm = float(standard_info["humidity_soil"])
            env_name = "Humidity, Moist Air, Soil Contact"
        else:
            permissible_limit_mm = float(standard_info["dry_air_protected"])
            env_name = "Dry Air or Protective Coating"

        if depth_status in ["unknown", "not_assessed"]:
            compliance_status = "requires_review"
            status_explanation = (
                f"Surface crack width ({estimated_aperture_mm} mm) evaluated under {standard_info['name']}. "
                f"Permissible limit for {env_name} is {permissible_limit_mm} mm. "
                "However, full structural compliance cannot be certified without internal crack depth and reinforcement cover data."
            )
        elif estimated_aperture_mm <= permissible_limit_mm and not visible_spalling and not visible_corrosion:
            compliance_status = "provisionally_consistent"
            status_explanation = (
                f"Measured surface aperture ({estimated_aperture_mm} mm) is within the {standard_info['name']} serviceability limit of {permissible_limit_mm} mm for {env_name}. "
                "Provisional status assigned pending internal depth confirmation."
            )
        else:
            compliance_status = "potential_non_conformance"
            status_explanation = (
                f"Measured surface aperture ({estimated_aperture_mm} mm) exceeds the {standard_info['name']} threshold of {permissible_limit_mm} mm for {env_name}, "
                "or associated distress (spalling/corrosion) indicates potential non-conformance."
            )

        all_standards_comparison = {}
        for code_key, code_data in self.STANDARDS_LIMITS.items():
            limit_val = float(code_data["humidity_soil"] if "humid" in env_lower else (code_data["deicing_marine"] if "marine" in env_lower else code_data["dry_air_protected"]))
            all_standards_comparison[code_key] = {
                "name": str(code_data["name"]),
                "limit_mm": float(limit_val),
                "compliant": bool(estimated_aperture_mm <= limit_val)
            }

        compliance_details = {
            "status": compliance_status,
            "standard_code": selected_standard_key,
            "standard_name": str(standard_info["name"]),
            "standard_category": "current_standard",
            "relevant_criterion": f"Maximum Permissible Surface Crack Width for {env_name}",
            "observed_value": f"{estimated_aperture_mm} mm surface width ({pattern})",
            "reference_value": f"{permissible_limit_mm} mm maximum threshold",
            "explanation": status_explanation,
            "missing_information": "Internal crack depth (NDT UPV/Impact-Echo), concrete cover thickness, and structural load history.",
            "multi_standard_comparison": all_standards_comparison
        }

        plain_language = (
            f"The image shows a visible surface crack approximately {estimated_aperture_mm} mm wide at its widest point. "
            f"This measurement describes the surface opening only. Evaluated against {standard_info['name']} (limit: {permissible_limit_mm} mm). "
            f"The image does not show how deep the crack extends into the concrete or whether internal steel reinforcement is affected. "
            f"{'Because spalling or rust staining was noted, further professional physical inspection is advised.' if (visible_spalling or visible_corrosion) else 'A physical inspection is recommended if moisture or structural loads increase.'}"
        )

        aci_compliance_legacy = {
            "water_retaining": bool(estimated_aperture_mm <= float(self.STANDARDS_LIMITS["ACI"]["water_retaining"])),
            "deicing_marine": bool(estimated_aperture_mm <= float(self.STANDARDS_LIMITS["ACI"]["deicing_marine"])),
            "humidity_soil": bool(estimated_aperture_mm <= float(self.STANDARDS_LIMITS["ACI"]["humidity_soil"])),
            "dry_air_protected": bool(estimated_aperture_mm <= float(self.STANDARDS_LIMITS["ACI"]["dry_air_protected"]))
        }

        return {
            "severity": str(severity),
            "estimated_width": f"{min_aperture_mm} - {estimated_aperture_mm} mm",
            "max_aperture_mm": float(estimated_aperture_mm),
            "affected_area": str(area_pct_str),
            "recommendation": str(recommendation),
            "aci_compliance": aci_compliance_legacy,
            "crack_depth_status": str(depth_status),
            "crack_depth_explanation": str(depth_explanation),
            "evidence_sufficiency": evidence_sufficiency,
            "assessment_breakdown": assessment_breakdown,
            "compliance_details": compliance_details,
            "plain_language_explanation": str(plain_language),
            "multi_factor_metrics": {
                "crack_width_mm": float(estimated_aperture_mm),
                "crack_length_mm": float(total_length_mm),
                "crack_area_mm2": float(total_area_mm2),
                "crack_density_pct": float(area_pct),
                "crack_count": int(crack_count),
                "crack_pattern": str(pattern),
                "member_type": str(member_desc),
                "element_criticality": str(element_criticality),
                "proximity_to_supports": str(proximity_to_supports),
                "visible_spalling": bool(visible_spalling),
                "visible_corrosion": bool(visible_corrosion),
                "historical_progression": str(progression_note),
                "standard_code": str(selected_standard_key)
            },
            "unsupported_claims_disclaimer": "Surface condition appears consistent with selected criteria, but overall structural safety cannot be established from image analysis alone."
        }

    def _build_empty_assessment(
        self,
        member_type: Optional[str] = None,
        crack_depth_status: Optional[str] = "unknown",
        standard_code: Optional[str] = "ACI"
    ) -> Dict[str, Any]:
        standard_key = (standard_code or "ACI").upper()
        if standard_key not in self.STANDARDS_LIMITS:
            standard_key = "ACI"
        std_info = self.STANDARDS_LIMITS[standard_key]

        return {
            "severity": "low",
            "estimated_width": "0.0 mm",
            "max_aperture_mm": 0.0,
            "affected_area": "0.0%",
            "recommendation": "Routine inspection recommended. No surface crack distress identified in scanned region.",
            "aci_compliance": {
                "water_retaining": True,
                "deicing_marine": True,
                "humidity_soil": True,
                "dry_air_protected": True
            },
            "crack_depth_status": "surface_only",
            "crack_depth_explanation": "No surface crack discontinuities detected. Internal concrete condition presumed intact based on surface visual.",
            "evidence_sufficiency": {
                "status": "sufficient_for_surface_assessment",
                "missing_factors": [],
                "summary": "Surface image clear with no observable crack defects."
            },
            "assessment_breakdown": {
                "observation": "Zero crack fissures detected.",
                "context": f"Element: {member_type or 'Concrete Surface'}.",
                "deterioration": "No spalling or surface corrosion observed.",
                "assessment": f"Surface condition is intact under {std_info['name']}. No structural surface distress present."
            },
            "compliance_details": {
                "status": "verified",
                "standard_code": standard_key,
                "standard_name": str(std_info["name"]),
                "standard_category": "current_standard",
                "relevant_criterion": "Surface Discontinuity Scan",
                "observed_value": "0.0 mm surface width",
                "reference_value": "No crack defects",
                "explanation": f"No surface cracks detected exceeding minimum resolution under {std_info['name']}.",
                "missing_information": "None for surface visual."
            },
            "plain_language_explanation": "No visible cracks were detected in this image. The surface appears intact.",
            "multi_factor_metrics": {
                "crack_width_mm": 0.0,
                "crack_length_mm": 0.0,
                "crack_area_mm2": 0.0,
                "crack_density_pct": 0.0,
                "crack_count": 0,
                "crack_pattern": "None",
                "member_type": str(member_type or "Concrete Surface"),
                "element_criticality": "unspecified",
                "proximity_to_supports": "unspecified",
                "visible_spalling": False,
                "visible_corrosion": False,
                "historical_progression": "No previous crack",
                "standard_code": standard_key
            },
            "unsupported_claims_disclaimer": "Surface condition appears consistent with selected criteria, but overall structural safety cannot be established from image analysis alone."
        }
