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
        standard_code: Optional[str] = "ACI",
        # Building Profile & Age Context Inputs
        building_name: Optional[str] = None,
        building_type: Optional[str] = "residential",
        construction_year: Optional[int] = None,
        building_age_years: Optional[float] = None,
        age_verification: Optional[str] = "unknown",
        inspection_date: Optional[str] = None,
        structural_system: Optional[str] = "unknown",
        structural_material: Optional[str] = "reinforced_concrete",
        member_importance: Optional[str] = None,
        repair_history: Optional[str] = None,
        last_major_inspection_date: Optional[str] = None,
        last_repair_date: Optional[str] = None,
        previous_crack_repairs: Optional[str] = "unknown",
        previous_water_leakage: bool = False,
        known_reinforcement_corrosion: bool = False,
        known_spalling_delamination: bool = False,
        known_settlement: bool = False,
        damaging_events: Optional[str] = "none",
        maintenance_condition: Optional[str] = "unknown",
        environmental_exposure: Optional[str] = None
    ) -> Dict[str, Any]:
        from datetime import datetime
        selected_standard_key = (standard_code or "ACI").upper()
        if selected_standard_key not in self.STANDARDS_LIMITS:
            selected_standard_key = "ACI"
        standard_info = self.STANDARDS_LIMITS[selected_standard_key]

        effective_criticality = member_importance or element_criticality or "primary"
        effective_env = environmental_exposure or environment or "unknown"

        # 1. Parse inspection date and determine historical inspection year
        inspection_year = datetime.now().year
        if inspection_date:
            try:
                insp_str = str(inspection_date).strip()
                if "-" in insp_str:
                    inspection_year = int(insp_str.split("-")[0])
                else:
                    inspection_year = int(insp_str[:4])
            except Exception:
                inspection_year = datetime.now().year

        # 2. Age Calculation & Validation
        calculated_age: Optional[float] = None
        age_status_verification = age_verification or "unknown"
        is_invalid_future_year = False

        parsed_building_age: Optional[float] = None
        if building_age_years is not None:
            try:
                parsed_building_age = float(building_age_years)
            except (ValueError, TypeError):
                parsed_building_age = None

        if construction_year is not None:
            if construction_year > inspection_year:
                is_invalid_future_year = True
                calculated_age = None
                age_status_verification = "invalid_future_year"
            else:
                calculated_age = float(inspection_year - construction_year)
                if age_status_verification in ["unknown", ""]:
                    age_status_verification = "documented"
        elif parsed_building_age is not None and parsed_building_age >= 0:
            calculated_age = parsed_building_age
            if age_status_verification in ["unknown", ""]:
                age_status_verification = "estimated"

        building_profile_dict = {
            "building_name": building_name,
            "building_type": building_type or "residential",
            "construction_year": construction_year,
            "age_years": calculated_age,
            "building_age_years": int(calculated_age) if calculated_age is not None else None,
            "age_verification": age_status_verification,
            "inspection_date": inspection_date or datetime.now().strftime("%Y-%m-%d"),
            "structural_system": structural_system or "unknown",
            "structural_material": structural_material or "reinforced_concrete",
            "structural_member": member_type or "wall",
            "member_importance": effective_criticality,
            "repair_history": repair_history,
            "last_major_inspection_date": last_major_inspection_date,
            "last_repair_date": last_repair_date,
            "previous_crack_repairs": previous_crack_repairs or "unknown",
            "previous_water_leakage": bool(previous_water_leakage),
            "known_reinforcement_corrosion": bool(known_reinforcement_corrosion),
            "known_spalling_delamination": bool(known_spalling_delamination),
            "known_settlement": bool(known_settlement),
            "damaging_events": damaging_events or "none",
            "maintenance_condition": maintenance_condition or "unknown",
            "environmental_exposure": effective_env
        }

        # Calibrated Optical Scale (Defaulting to 0.15m macro inspection FOV)
        mm_per_pixel = (assumed_field_width_m * 1000.0) / max(image_width, 1)

        if not polygons:
            return self._build_empty_assessment(
                member_type=member_type,
                crack_depth_status=crack_depth_status,
                standard_code=selected_standard_key,
                building_profile=building_profile_dict,
                inspection_year=inspection_year,
                calculated_age=calculated_age,
                age_status_verification=age_status_verification,
                is_invalid_future_year=is_invalid_future_year
            )

        # 3. Component B: Surface Measurement (Width, Length, Area, Density, Pattern)
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

        # 4. Crack Depth / Internal Condition Handling (STRICT SEPARATION)
        depth_status = str(crack_depth_status or "unknown")
        depth_explanation = (
            f"Measured surface crack width: {estimated_aperture_mm} mm. "
            "Crack depth cannot be established from surface optical images alone. "
            "Internal structural damage is not calculated from building age, surface width, or AI confidence. "
            "Structural significance therefore cannot be certified from surface imaging alone."
        )

        # 5. Component D: Deterioration Indicators
        is_expanding = False
        if previous_width_mm is not None and estimated_aperture_mm > (previous_width_mm + 0.1):
            is_expanding = True

        deterioration_indicators: List[str] = []
        if visible_spalling or known_spalling_delamination:
            deterioration_indicators.append("Visible concrete spalling or surface delamination")
        if visible_corrosion or known_reinforcement_corrosion:
            deterioration_indicators.append("Known or visible rebar corrosion staining")
        if previous_water_leakage or any(w in effective_env.lower() for w in ["moist", "marine", "humid", "leak", "damp"]):
            deterioration_indicators.append("Persistent moisture exposure or active water ingress")
        if known_settlement:
            deterioration_indicators.append("Foundation settlement or differential movement distress")
        if is_expanding:
            deterioration_indicators.append(f"Active crack width growth (>0.1 mm above historical baseline)")
        if damaging_events and damaging_events.lower() not in ["none", ""]:
            deterioration_indicators.append(f"Recorded damaging event ({damaging_events})")

        # 6. Component E: Evidence Sufficiency Evaluation
        missing_factors = []
        if depth_status in ["unknown", "not_assessed", "surface_only"]:
            missing_factors.append("internal_crack_depth_scan")
        if not member_type or member_type == "custom":
            missing_factors.append("verified_structural_member_type")
        if previous_width_mm is None:
            missing_factors.append("historical_progression_baseline")
        if construction_year is None and calculated_age is None:
            missing_factors.append("building_construction_age_documentation")
        if is_invalid_future_year:
            missing_factors.append("valid_construction_year")
        if maintenance_condition in ["unknown", None, ""]:
            missing_factors.append("structural_maintenance_history")

        if len(missing_factors) >= 1:
            evidence_sufficiency = {
                "status": "insufficient_for_engineering_assessment",
                "missing_factors": missing_factors,
                "summary": "Surface evidence captured cleanly, but full structural engineering interpretation requires additional contextual, age-verification, or NDT inspection data."
            }
        else:
            evidence_sufficiency = {
                "status": "sufficient_for_surface_assessment",
                "missing_factors": [],
                "summary": "Sufficient surface and contextual evidence present for preliminary engineering surface evaluation."
            }

        # 7. Multi-Factor Severity Logic (Physical Evidence Driven — NOT an arbitrary age multiplier)
        severity_points = 0
        
        if estimated_aperture_mm >= 0.75:
            severity_points += 3
        elif estimated_aperture_mm >= 0.30:
            severity_points += 2
        else:
            severity_points += 1

        is_primary = (effective_criticality == "primary")
        near_support = (proximity_to_supports in ["near_support", "connection"])
        if is_primary and near_support:
            severity_points += 2
        elif is_primary or near_support:
            severity_points += 1

        if visible_spalling or known_spalling_delamination:
            severity_points += 2
        if visible_corrosion or known_reinforcement_corrosion:
            severity_points += 2
        if is_expanding:
            severity_points += 2
        if known_settlement:
            severity_points += 1

        if severity_points >= 6:
            severity = "high"
        elif severity_points >= 3:
            severity = "medium"
        else:
            severity = "low"

        # 8. Component F: Age & Deterioration Context Synthesis
        has_active_distress = bool(deterioration_indicators)
        has_moisture = any(w in effective_env.lower() for w in ["moist", "marine", "humid", "leak", "damp"]) or previous_water_leakage
        is_older_building = (calculated_age is not None and calculated_age >= 25.0)
        is_early_age = (calculated_age is not None and calculated_age <= 5.0)

        if is_invalid_future_year or (calculated_age is None and age_status_verification == "unknown"):
            age_context_status = "insufficient_historical_information"
            status_label = "Insufficient Historical Information"
            age_influence_summary = (
                "Building construction year and historical maintenance records are unverified. "
                "Assessment is strictly based on observable surface geometry and visible distress."
            )
        elif is_early_age and (severity in ["medium", "high"] or estimated_aperture_mm >= 0.30 or near_support or has_active_distress or known_settlement):
            age_context_status = "early_age_construction_defect_suspected"
            status_label = "Early-Age Construction / Structural Defect Suspected"
            age_influence_summary = (
                f"Structure is in its early service life ({int(calculated_age)} years). Under ACI 224.1R-07 (Sections 1.2-1.3) and ACI CODE-562-25 Section 6.2, "
                f"a crack aperture of {estimated_aperture_mm} mm in an early-age concrete member is atypical of normal long-term weathering. "
                "This condition strongly indicates construction-phase anomalies, including premature formwork de-shoring, "
                "inadequate moist curing or thermal shrinkage restraint, early structural overloading, or differential foundation settlement. "
                "Forensic review of construction QA records (cube test results, pour logs, curing certificates) is recommended."
            )
        elif is_older_building and has_active_distress:
            age_context_status = "potential_age_related_distress"
            status_label = "Potential Age-Related Deterioration Indicators Present"
            age_influence_summary = (
                f"Asset is approximately {int(calculated_age)} years old with active deterioration distress "
                f"({', '.join(deterioration_indicators[:2])}). "
                "Long-term environmental exposure and cumulative aging mechanisms (concrete carbonation depth exceeding cover, chloride penetration, rebar depassivation) "
                "are relevant contextual factors under ACI CODE-562-25 Section 6.2."
            )
        elif has_moisture and (has_active_distress or estimated_aperture_mm >= 0.25):
            age_context_status = "further_deterioration_assessment_recommended"
            status_label = "Further Deterioration Assessment Recommended"
            age_influence_summary = (
                f"Asset age ({f'{int(calculated_age)} years' if calculated_age is not None else 'estimated'}) in conjunction with persistent moisture "
                "or localized structural proximity warrants durability testing (phenolphthalein carbonation depth, half-cell corrosion potential) "
                "to evaluate internal rebar protection."
            )
        elif calculated_age is not None and not has_active_distress and estimated_aperture_mm < 0.30:
            age_context_status = "context_documented"
            status_label = "Context Documented"
            if is_early_age:
                age_influence_summary = (
                    f"Structure is early-age ({int(calculated_age)} years). Surface crack remains narrow ({estimated_aperture_mm} mm) and stable with no observed "
                    "spalling, corrosion, or settlement distress. Fissure is consistent with non-structural plastic or drying shrinkage within ACI 224R-01 limits."
                )
            else:
                age_influence_summary = (
                    f"Building age ({int(calculated_age)} years) is documented. Surface crack remains narrow and stable with no observed "
                    "corrosion, spalling, or moisture distress. Building age alone does not elevate structural severity."
                )
        else:
            age_context_status = "no_age_specific_conclusion_supported"
            status_label = "No Age-Specific Conclusion Supported by Available Evidence"
            age_influence_summary = (
                "Available observations and historical evidence do not establish an age-specific structural deterioration mechanism. "
                "Condition assessment reflects observed physical measurements."
            )

        location_desc = proximity_to_supports.replace('_', ' ').capitalize() if proximity_to_supports else "Unspecified location"
        member_desc = str(member_type or "Structural Concrete Surface")
        
        progression_note = (
            f"Active width expansion recorded (previously {previous_width_mm} mm)."
            if is_expanding
            else ("Historical baseline unavailable." if previous_width_mm is None else f"Consistent with historical measurement ({previous_width_mm} mm).")
        )

        remediation_spec = self.generate_remediation_specification(
            structural_material=structural_material,
            member_type=member_type,
            building_type=building_type,
            structural_system=structural_system,
            crack_pattern=pattern,
            severity=severity,
            estimated_aperture_mm=estimated_aperture_mm,
            environmental_exposure=effective_env,
            previous_water_leakage=previous_water_leakage,
            is_expanding=is_expanding,
            visible_spalling=bool(visible_spalling or known_spalling_delamination),
            visible_corrosion=bool(visible_corrosion or known_reinforcement_corrosion),
            is_early_age=bool(is_early_age),
            near_support=near_support,
            is_primary=is_primary
        )
        recommendation = remediation_spec["summary_recommendation"]

        if age_context_status == "early_age_construction_defect_suspected":
            engineering_rationale = (
                f"The measured surface crack width ({estimated_aperture_mm} mm) is evaluated on a {member_desc.lower()} "
                f"({'primary load-bearing' if is_primary else 'secondary element'}) in a {location_desc.lower()} on a newly constructed structure "
                f"({int(calculated_age)} years old). Under ACI 224.1R-07 Section 1.2-1.3, ACI CODE-562-25 Section 6.2, and IS 456 Clause 35.3.2, "
                "severe cracking in early service life points to potential construction defects (premature shore stripping, poor curing, construction overload, or settlement). "
                f"{'Associated distress indicators (' + ', '.join(deterioration_indicators) + ') reinforce the urgency of construction-phase forensic audit. ' if deterioration_indicators else 'Internal rebar cover and depth must be verified by NDT.'}"
            )
            if "EARLY-AGE CONSTRUCTION DEFECT AUDIT" not in recommendation:
                recommendation += (
                    " EARLY-AGE CONSTRUCTION DEFECT AUDIT: Because the structure is <= 5 years old, audit contractor concrete batching records, "
                    "7-day and 28-day cylinder/cube compressive test logs, formwork stripping records (IS 456 Cl. 11 / ACI 347), and check foundation levels for differential settlement."
                )
        else:
            engineering_rationale = (
                f"The measured surface crack width ({estimated_aperture_mm} mm) is one component of this assessment. "
                f"The building's age ({f'{int(calculated_age)} years' if calculated_age is not None else 'unverified'}) provides context, "
                "but does not independently determine severity. "
                f"Evaluated on a {member_desc.lower()} ({'primary load-bearing' if is_primary else 'secondary element'}) in a {location_desc.lower()}. "
                f"{'Associated distress indicators (' + ', '.join(deterioration_indicators) + ') warrant further engineering investigation. ' if deterioration_indicators else 'No active spalling or corrosion distress was observed. '}"
                f"Crack depth and internal reinforcement condition have not been established from surface visual imagery."
            )

        standards_consulted = [
            {
                "standard": "ACI CODE-562-25",
                "title": "Assessment, Repair, and Rehabilitation of Existing Concrete Structures",
                "scope": "Existing structural condition assessment, chronology evaluation, and repair criteria",
                "verification_status": "Framework Reference"
            },
            {
                "standard": "ACI 224.1R-07",
                "title": "Causes, Evaluation, and Repair of Cracks in Concrete Structures",
                "scope": "Diagnostic root causes: plastic shrinkage, thermal contraction, formwork removal, construction overload",
                "verification_status": "Diagnostic Root-Cause Reference"
            },
            {
                "standard": "ACI 224R-01",
                "title": "Control of Cracking in Concrete Structures",
                "scope": "Permissible surface crack width comparator limits for serviceability",
                "verification_status": "Surface Comparator Reference"
            },
            {
                "standard": "IS 456:2000 & IS 15988:2013",
                "title": "Plain and Reinforced Concrete / Seismic Evaluation & Strengthening of Existing RC Buildings",
                "scope": "Permissible crack widths (Cl. 35.3.2), stripping times (Cl. 11), and structural health assessment",
                "verification_status": "Applicable Jurisdiction Standard" if selected_standard_key == "IS_456" else "Comparative Reference"
            }
        ]

        age_deterioration_context = {
            "status": age_context_status,
            "status_label": status_label,
            "construction_year": construction_year,
            "inspection_year": inspection_year,
            "age_at_inspection_years": calculated_age,
            "age_at_inspection": int(calculated_age) if calculated_age is not None else None,
            "age_verification": age_status_verification,
            "environmental_exposure": effective_env,
            "maintenance_condition": maintenance_condition or "unknown",
            "observed_deterioration_indicators": deterioration_indicators,
            "historical_progression": str(progression_note),
            "missing_historical_information": missing_factors,
            "missing_information": missing_factors,
            "age_influence_summary": age_influence_summary,
            "engineering_rationale": engineering_rationale,
            "engineering_reasoning": engineering_rationale,
            "standards_consulted": standards_consulted,
            "disclaimer": "Building age is contextual information and is not, by itself, a measure of structural safety or crack severity.",
            "context_disclaimer": "Building age is contextual information and is not, by itself, a measure of structural safety or crack severity."
        }

        # 9. Assessment Breakdown
        assessment_breakdown = {
            "observation": f"Maximum surface aperture: {estimated_aperture_mm} mm. Estimated length: {total_length_mm} mm ({crack_count} fissure(s), {pattern}).",
            "context": f"Element: {member_desc} ({'Primary Load-Bearing' if is_primary else 'Secondary Element'}). Location: {location_desc}. Building Age: {f'{int(calculated_age)} yrs' if calculated_age is not None else 'Unverified'}.",
            "deterioration": f"Visible Spalling: {'Yes' if (visible_spalling or known_spalling_delamination) else 'None'}. Corrosion: {'Yes' if (visible_corrosion or known_reinforcement_corrosion) else 'None'}. Progression: {progression_note}.",
            "assessment": (
                f"Condition category assigned based on multi-factor physical synthesis (Geometry + Structural Location + Visible Distress). "
                f"Building age context: {status_label}. "
                f"Evaluated against standard: {standard_info['name']}. Surface visual only; internal depth unverified."
            )
        }

        # 10. Multi-Code Compliance
        env_lower = effective_env.lower()
        if "marine" in env_lower or "salt" in env_lower or "severe" in env_lower or "coastal" in env_lower:
            permissible_limit_mm = float(standard_info["deicing_marine"])
            env_name = "Deicing Chemicals & Seawater Spray"
        elif "humid" in env_lower or "soil" in env_lower or "moist" in env_lower or "damp" in env_lower or "leak" in env_lower:
            permissible_limit_mm = float(standard_info["humidity_soil"])
            env_name = "Humidity, Moist Air, Soil Contact"
        else:
            permissible_limit_mm = float(standard_info["dry_air_protected"])
            env_name = "Dry Air or Protective Coating"

        if depth_status in ["unknown", "not_assessed", "surface_only"]:
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
            f"Building age: {f'{int(calculated_age)} years' if calculated_age is not None else 'unknown'}. "
            f"The image does not show how deep the crack extends into the concrete or whether internal steel reinforcement is affected. "
            f"{'Because spalling or rust staining was noted, further professional physical inspection is advised.' if (visible_spalling or visible_corrosion or known_reinforcement_corrosion) else 'A physical inspection is recommended if moisture or structural loads increase.'}"
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
            "remediation_specification": remediation_spec,
            "aci_compliance": aci_compliance_legacy,
            "crack_depth_status": str(depth_status),
            "crack_depth_explanation": str(depth_explanation),
            "evidence_sufficiency": evidence_sufficiency,
            "assessment_breakdown": assessment_breakdown,
            "compliance_details": compliance_details,
            "plain_language_explanation": str(plain_language),
            "building_profile": building_profile_dict,
            "age_deterioration_context": age_deterioration_context,
            "multi_factor_metrics": {
                "crack_width_mm": float(estimated_aperture_mm),
                "crack_length_mm": float(total_length_mm),
                "crack_area_mm2": float(total_area_mm2),
                "crack_density_pct": float(area_pct),
                "crack_count": int(crack_count),
                "crack_pattern": str(pattern),
                "member_type": str(member_desc),
                "element_criticality": str(effective_criticality),
                "proximity_to_supports": str(proximity_to_supports),
                "visible_spalling": bool(visible_spalling or known_spalling_delamination),
                "visible_corrosion": bool(visible_corrosion or known_reinforcement_corrosion),
                "historical_progression": str(progression_note),
                "standard_code": str(selected_standard_key),
                "building_age_years": calculated_age
            },
            "unsupported_claims_disclaimer": "Surface condition appears consistent with selected criteria, but overall structural safety cannot be established from image analysis alone."
        }

    @classmethod
    def generate_remediation_specification(
        cls,
        structural_material: Optional[str] = None,
        member_type: Optional[str] = None,
        building_type: Optional[str] = None,
        structural_system: Optional[str] = None,
        crack_pattern: str = "longitudinal",
        severity: str = "medium",
        estimated_aperture_mm: float = 0.35,
        environmental_exposure: Optional[str] = None,
        previous_water_leakage: bool = False,
        is_expanding: bool = False,
        visible_spalling: bool = False,
        visible_corrosion: bool = False,
        is_early_age: bool = False,
        near_support: bool = False,
        is_primary: bool = True
    ) -> Dict[str, Any]:
        """
        Synthesize tailored civil engineering remediation specification and prescribed structural action
        governed by:
        1. Material (Asphalt/Bitumen vs Masonry vs Prestressed PT vs Reinforced Concrete).
        2. Location / Member Type (Road surface vs Bridge deck vs Column/Transfer girder vs Retaining wall/Foundation vs Slab).
        3. Crack Morphology & Behavior (Moving/active vs Dormant flexural vs Alligator/fatigue vs Hairline shrinkage).
        4. Environmental State (Active water ingress/hydrostatic vs Dry service).
        """
        mat_str = str(structural_material or "").lower()
        mem_str = str(member_type or "").lower()
        bld_str = str(building_type or "").lower()
        sys_str = str(structural_system or "").lower()
        env_str = str(environmental_exposure or "").lower()
        pat_str = str(crack_pattern or "").lower()

        is_asphalt = any(k in mat_str for k in ["asphalt", "bitumen", "bituminous"]) or \
                     any(k in mem_str for k in ["road", "pavement", "asphalt", "wearing_course", "highway"]) or \
                     any(k in bld_str for k in ["road", "highway", "pavement"])

        is_masonry = any(k in mat_str for k in ["masonry", "brick", "stone", "blockwork"]) or \
                     any(k in sys_str for k in ["masonry", "bearing_masonry"]) or \
                     "masonry" in mem_str or "brick" in mem_str

        is_pt = any(k in mat_str for k in ["prestressed", "post_tension", "post-tension", "pt_"]) or \
                any(k in sys_str for k in ["prestressed", "post_tension"])

        is_wet = previous_water_leakage or \
                 any(k in env_str for k in ["moist", "water", "leak", "groundwater", "damp", "marine"]) or \
                 any(k in mem_str for k in ["retaining_wall", "basement", "foundation", "water_tank", "culvert"])

        # -------------------------------------------------------------
        # CATEGORY 1: ASPHALT & BITUMINOUS ROADWAY / PAVEMENT SURFACES
        # -------------------------------------------------------------
        if is_asphalt:
            if any(k in pat_str for k in ["alligator", "map", "network", "fatigue"]) or (severity == "high" and estimated_aperture_mm >= 5.0):
                protocol_title = "AASHTO PP 44 / ISSA A143 Full-Depth Pavement Milling & Patching Protocol"
                standard = "AASHTO PP 44, ASTM D692 & ISSA A143"
                mat_category = "Asphalt Concrete / Bituminous Pavement"
                material_spec = (
                    "Hot Mix Asphalt (HMA) Superpave 12.5mm surface course and 19.0mm intermediate binder course conforming to ASTM D3515 / ASTM D692 "
                    "over compacted crushed aggregate base (CBR > 80%). For localized fatigue zones: ISSA A143 micro-surfacing emulsion with polymer-modified asphalt. "
                    "Rigid epoxy injection is STRICTLY PROHIBITED on flexible pavement."
                )
                actions = [
                    "Traffic Safety: Establish MUTCD Part 6 temporary traffic control zone, warning signs, and lane closure taper.",
                    "Cold Milling: Plane and mill deteriorated fatigue-cracked asphalt down to sound aggregate base course (minimum 50mm–100mm depth).",
                    "Subbase Inspection & Compaction: Proof-roll and re-compact granular base; replace soft subgrade pockets with crushed stone.",
                    "Tack Coat Application: Spray cationic rapid-setting asphalt emulsion tack coat (ASTM D2397 Grade CRS-2) at 0.35–0.45 L/m² to milled vertical sidewalls and base.",
                    "HMA Inlay & Compaction: Place hot-mix asphalt in lifts not exceeding 50mm compacted thickness; compact to 93%–97% Rice theoretical maximum density using vibratory steel-wheel and pneumatic rollers.",
                    "Joint Sealing: Edge-seal perimeter construction joints with hot-poured rubberized sealant (ASTM D6690 Type II)."
                ]
                equipment = [
                    "Cold milling planer machine",
                    "High-velocity compressed air lance",
                    "Tack coat distributor spray bar",
                    "Vibratory tandem steel-wheel compactor (8–10 ton)",
                    "MUTCD traffic arrow boards and channelizer cones"
                ]
                safety = "ACTIVE ROADWAY SAFETY HAZARD: High-speed vehicular traffic hazard. Strictly enforce MUTCD buffer zones and shadow vehicles with truck-mounted attenuators (TMA). High-temperature asphalt placement at 145°C–160°C."
                preventive = "Conduct annual post-winter pavement audits; inspect joint seals for debonding to prevent water intrusion into the roadbed."
                summary_rec = "PAVEMENT REHABILITATION: Network fatigue cracking on roadway pavement indicates subbase deflection. Surface sealing alone will fail; execute cold-milling and full-depth HMA patching conforming to AASHTO PP 44 and ASTM D692 with MUTCD traffic control."

            elif estimated_aperture_mm < 2.0 and severity == "low" and not is_expanding:
                protocol_title = "ISSA A105 Polymer-Modified Bituminous Surface Fog Seal Protocol"
                standard = "ISSA A105 & ASTM D977"
                mat_category = "Asphalt Concrete / Bituminous Pavement"
                material_spec = (
                    "Polymer-modified cationic asphalt emulsion fog seal (ASTM D977 Grade CSS-1h or CQS-1h), diluted 50:50 with water, "
                    "incorporating elastomeric latex polymers to enrich aged oxidized binder."
                )
                actions = [
                    "Surface Sweeping: Rotary broom and high-pressure dry air blast to remove roadway detritus and dust.",
                    "Fog Spray Application: Uniformly spray polymer-modified asphalt emulsion at 0.45–0.70 L/m² via calibrated distributor bar.",
                    "Penetration & Cure: Allow 2–3 hours cure time under warm ambient conditions (>15°C) before opening to traffic.",
                    "Skid-Resistance Sanding: Lightly broadcast dry 30-mesh silica sand at pedestrian crossings or critical intersections if needed."
                ]
                equipment = [
                    "Rotary power street broom",
                    "Pressurized emulsion distributor spray truck",
                    "Traffic channelizing cones"
                ]
                safety = "SKID REDUCTION ADVISORY: Newly sprayed fog seals have temporarily reduced wet-pavement skid resistance. Maintain traffic control until tack-free."
                preventive = "Re-evaluate pavement texture in 24 months to assess binder rejuvenation."
                summary_rec = "ROUTINE ROAD MAINTENANCE: Narrow surface checking on asphalt surface. Apply polymer-modified asphalt fog seal complying with ISSA A105 to rejuvenate bitumen binder and halt progressive oxidation."

            else:
                protocol_title = "ASTM D6690 / AASHTO M 324 Hot-Applied Elastomeric Asphalt Crack Seal Protocol"
                standard = "ASTM D6690 Type I/II/IV & AASHTO M 324"
                mat_category = "Asphalt Concrete / Bituminous Pavement"
                material_spec = (
                    "Single-component, hot-applied polymer-modified rubberized bituminous crack sealant conforming to ASTM D6690 Type II (AASHTO M 324). "
                    "Pouring temperature 185°C–195°C; resilience minimum 30%; cone penetration 50–90 at 25°C; low-temperature flexibility at -18°C. "
                    "Rigid structural epoxy is STRICTLY PROHIBITED on flexible pavement."
                )
                actions = [
                    "Traffic Management: Set up temporary lane closure complying with MUTCD Chapter 6.",
                    "Reservoir Routing: For cracks 3mm–19mm wide, machine-rout a clean 12mm×12mm or 19mm×19mm rectangular reservoir with vertical sidewalls using a pavement crack router.",
                    "Heat Lance Dehydration: Blast fissure with a hot compressed air lance (>1000°C air stream at 100 psi) to vaporize all internal moisture and pre-warm asphalt sidewalls for optimal bonding.",
                    "Hot Sealant Injection: Pump hot rubberized asphalt sealant at 190°C directly from oil-jacketed melter into reservoir from bottom up.",
                    "Overband Squeegee Strike-Off: Form a smooth 40mm–50mm wide overband cap with a maximum 1.5mm profile above pavement using an elastomeric squeegee shoe.",
                    "Detackifier / Sanding: Apply liquid detackifying agent or broadcast fine manufactured sand to eliminate vehicle tire pickup before opening to traffic."
                ]
                equipment = [
                    "Double-boiler oil-jacketed asphalt sealant melter with continuous agitator",
                    "Hot compressed air heat lance (HCA)",
                    "Rotary pavement crack router with carbide star cutters",
                    "V-shaped silicon strike-off squeegee shoe",
                    "MUTCD traffic safety arrow board"
                ]
                safety = "HOT BITUMEN & TRAFFIC HAZARD: Operating temperature ~190°C can cause severe third-degree burns. Wear heat-resistant Kevlar/leather gloves, full face shield, long sleeves, and high-visibility safety vest."
                preventive = "Perform annual pre-winter pavement crack audits; inspect sealant bond along reservoir sidewalls after freeze-thaw cycles. Re-seal detached segments."
                summary_rec = "ROADWAY PRESERVATION: Machine-rout 12mm×12mm reservoir, heat-lance dehydrate, and inject hot-applied polymer-modified rubberized sealant complying with ASTM D6690 Type II / AASHTO M 324. Rigid epoxy is prohibited on flexible pavement."

        # -------------------------------------------------------------
        # CATEGORY 2: STRUCTURAL MASONRY / BRICKWORK
        # -------------------------------------------------------------
        elif is_masonry:
            protocol_title = "TMS 402/602 Helical Stainless Tie Stitching & ASTM C270 Repointing Protocol"
            standard = "TMS 402/602 & ASTM C270 / BRE Digest 359"
            mat_category = "Structural Brickwork / Load-Bearing Masonry"
            material_spec = (
                "Austenitic Grade 304 or 316 stainless steel helical tie bars (diameter 6mm–8mm, tensile strength >850 N/mm²), "
                "thixotropic non-shrink cementitious bonding grout (EN 1504-6), and breathable lime-cement mortar conforming to ASTM C270 Type N or O "
                "(matched to existing unit compressive strength to prevent edge spalling). High-modulus rigid epoxy is PROHIBITED (causes spalling of brick faces)."
            )
            actions = [
                "Joint Raking: Carefully rake out deteriorated bed-joint mortar to a depth of 20mm–25mm along cracked courses using diamond oscillating raking tools without cutting brick units.",
                "Helical Stitching Slots: For structural diagonal or stair-step cracks, cut continuous horizontal chase slots 30mm–40mm deep into bed joints extending 500mm beyond each side of the crack, spaced every 3–4 courses vertically.",
                "Dust Evacuation & Wetting: Vacuum out masonry dust and pre-wet joint slots to prevent premature moisture suction from repair grout.",
                "Helical Bar Embedment: Inject continuous bead of thixotropic non-shrink cementitious anchor grout into the rear of slot; press Grade 304/316 helical tie bar firmly into grout; encapsulate with secondary grout pass.",
                "Breathable Repointing: Repoint bed and perpendicular head joints with matching lime-cement mortar (ASTM C270 Type N), tooling joints to match historic building profile.",
                "Displacement Tell-Tale: Install calibrated two-axis polycarbonate tell-tale gauge across fissure to track seasonal thermal masonry movement."
            ]
            equipment = [
                "Oscillating mortar raking saw with HEPA vacuum dust shroud",
                "Pneumatic or manual grout applicator gun with flattened nozzle",
                "Helical bar installation insertion tool",
                "Stainless steel joint pointing trowel and jointer",
                "Calibrated mechanical crack displacement tell-tale"
            ]
            safety = "SILICA DUST & UNIT INTEGRITY WARNING: OSHA Table 1 HEPA dust extraction mandatory during joint raking. Do NOT use heavy pneumatic rotary hammer drills on unreinforced masonry. Never inject high-strength rigid epoxy into soft brick joints."
            preventive = "Inspect repointed joints and helical tie anchor zones semi-annually. Verify roof gutter and downspout discharge to eliminate water saturation of masonry piers."
            summary_rec = "MASONRY STABILIZATION: Install bed-joint helical Grade 304 stainless steel stitching ties embedded in thixotropic grout (TMS 402/602) and repoint with breathable lime mortar (ASTM C270 Type N). Do not use rigid epoxy."

        # -------------------------------------------------------------
        # CATEGORY 3: PRESTRESSED / POST-TENSIONED CONCRETE
        # -------------------------------------------------------------
        elif is_pt:
            protocol_title = "PTI DC80.1 / ACI 423.7 Precision Vacuum Epoxy Injection & Tendon Safeguard Protocol"
            standard = "ACI 423.7, PTI M55.1 & ACI CODE-562-25"
            mat_category = "Prestressed / Post-Tensioned Concrete (PT)"
            material_spec = (
                "High-modulus, ultra-low-viscosity 100% solids epoxy resin conforming to ASTM C881 Type I/IV Grade 1 (Class B/C), "
                "with viscosity <200 cPs at 23°C to ensure micro-crack penetration without requiring destructive high injection pressures. "
                "For unbonded tendon ducts: thixotropic polymer-modified corrosion-inhibiting cement grout complying with PTI M55.1 Class C."
            )
            actions = [
                "CRITICAL SAFETY — Tendon Mapping: Prior to any drilling or anchoring, perform high-frequency Ground Penetrating Radar (GPR 2.6 GHz) or covermeter scan to establish exact 3D coordinates and depth profiles of all high-strength prestressing tendons and live anchor zones.",
                "Zero-Drilling Zone Enforcement: Mechanical drilling or percussion hammer chipping into concrete within 150mm of active tendon ducts is STRICTLY PROHIBITED.",
                "Surface Port Mounting: Adhere surface-mounted injection ports directly over the crack fissure using thixotropic epoxy gel cap (ASTM C881 Type I Grade 3) without mechanical fastener anchors.",
                "Vacuum-Assisted Low-Pressure Injection: Execute vacuum-assisted or low-pressure injection (<0.2 MPa / 30 psi) starting from lowest elevation port until clear resin purges from adjacent port.",
                "Tendon Anchor Inspection: Inspect PT anchorage pocket caps for moisture intrusion, efflorescence, or tendon slippage signs.",
                "Post-Curing Acoustic Verification: Verify resin cure and test element with Ultrasonic Pulse Velocity (UPV) to verify monolithic shear continuity across tendon path."
            ]
            equipment = [
                "High-frequency GPR structural scanner (2.0–2.6 GHz)",
                "Vacuum-assisted positive-displacement epoxy proportioning pump",
                "Surface-mount flanged injection ports and port caps",
                "Ultrasonic Pulse Velocity (UPV) non-destructive testing transducer set"
            ]
            safety = "EXPLOSIVE STRAND FAILURE HAZARD: Prestressing tendons store massive kinetic energy (~70% of ultimate tensile strength). Any accidental tendon nick or severed wire can lead to catastrophic explosive failure of the entire slab or girder. Certified PT specialist mandatory."
            preventive = "Monitor tendon elongation and anchorage end-caps every 12 months. Conduct half-cell potential mapping if cracks are located within 300mm of post-tensioned tendon ducts."
            summary_rec = "POST-TENSIONED SAFEGUARD PROTOCOL: Conduct GPR tendon mapping before any contact. Strictly prohibit drilling within 150mm of tendon paths. Execute low-pressure vacuum epoxy injection (ASTM C881 Type IV Grade 1) under PTI DC80.1."

        # -------------------------------------------------------------
        # CATEGORY 4: WET / WATER-BEARING CONCRETE / BASEMENT WALLS
        # -------------------------------------------------------------
        elif is_wet:
            protocol_title = "EN 1504-5 / ACI 504R Hydrophilic Polyurethane Chemical Grout Water-Stopping Protocol"
            standard = "EN 1504-5 (Category D/S) & ACI 504R"
            mat_category = "Water-Bearing / Moisture-Exposed Reinforced Concrete"
            material_spec = (
                "Dual-component hydrophobic or hydrophilic expanding polyurethane (PU) injection resin conforming to EN 1504-5, "
                "expanding 8× to 15× upon water contact to form a permanent, dense, flexible closed-cell water-impermeable gasket. "
                "Followed by ASTM C881 structural epoxy injection if dry monolithic bond is required, and crystalline capillary waterproofing barrier conforming to ASTM C1583."
            )
            actions = [
                "Fissure Mapping & Flow Rate Evaluation: Locate active water weeping or pressurized infiltration points along crack length.",
                "Staggered Packer Drilling: Drill 14mm-diameter injection holes at 45° angle to the concrete face, spaced 150mm–200mm apart, alternating from opposite sides of the crack to intersect the fissure at member mid-depth.",
                "Packer Seating: Insert steel/brass mechanical high-pressure injection packers fitted with one-way ball-check valves; tighten to expand rubber sleeves against concrete boreholes.",
                "Water-Reactive Chemical Injection: Inject hydrophilic polyurethane resin at controlled pressures (50–120 bar) starting from lowest port until expanding foam exits the face and adjacent ports, shutting off active water ingress.",
                "Packer Removal & Cavity Plugging: After 24-hour polymerization, knock off packer stems and seal drill cavities with fast-setting non-shrink hydraulic plug mortar (ASTM C928).",
                "Surface Crystalline Protection: Apply slurry coat of deep-penetrating catalytic crystalline waterproofing coating over the repaired concrete zone."
            ]
            equipment = [
                "Electric high-pressure airless chemical injection pump (up to 200 bar)",
                "Heavy-duty SDS-Plus rotary hammer with 14mm carbide drill bits",
                "Steel mechanical packers with zerk fittings and one-way valves",
                "Safety splash goggles, chemical face shield, and butyl rubber gloves"
            ]
            safety = "HIGH-PRESSURE LIQUID HAZARD: Grout injection pressures reach up to 120 bar. Wear full face shield and chemical-resistant protective gear. Guard against sudden packer blowout or chemical spray into eyes."
            preventive = "Inspect basement walls and subterranean elements during high water-table / monsoon seasons. Monitor sump pumps and perimeter French drains to relieve hydrostatic head."
            summary_rec = "WATER-STOPPING CHEMICAL INJECTION: Active moisture ingress detected. Drill staggered 45° boreholes and inject expanding hydrophilic polyurethane resin (EN 1504-5 / ACI 504R) under controlled pressure to form a watertight seal."

        # -------------------------------------------------------------
        # CATEGORY 5: REINFORCED CONCRETE (DRY STRUCTURAL ELEMENTS)
        # -------------------------------------------------------------
        else:
            mat_category = "Structural Reinforced Concrete (RC)"

            # Subcase 5A: Active / Moving / Thermal Crack
            if is_expanding or any(k in pat_str for k in ["parallel", "joint"]):
                protocol_title = "ASTM C920 Elastomeric Polyurethane Routed Sealant Protocol (Active Movement)"
                standard = "ASTM C920 Type S/M, Class 25/50 & ACI 224.1R"
                material_spec = (
                    "Single-component or multi-component elastomeric polyurethane or polyurea joint sealant complying with ASTM C920 Type S or M, "
                    "Grade NS or P, Class 25 or 50, with movement capability ±25% to ±50%. Backer rod: closed-cell polyethylene foam (ASTM C1330 Type C). "
                    "Rigid epoxy is STRICTLY CONTRAINDICATED (will tear concrete)."
                )
                actions = [
                    "Reservoir Chasing: Rout a clean U-shaped groove 6mm–10mm wide by 10mm–12mm deep centered along the crack line using a crack-chaser diamond blade.",
                    "Dust Cleaning & Priming: Vacuum reservoir and apply compatible elastomeric polyurethane bonding primer to clean concrete sidewalls.",
                    "Bond-Breaker Installation: Install closed-cell polyethylene backer rod into reservoir base so sealant depth-to-width ratio is maintained at 1:1 or 1:2.",
                    "Sealant Placement: Gun elastomeric polyurethane sealant (ASTM C920 Class 35/50) into reservoir without entrapping air bubbles.",
                    "Tooling: Tool joint concave using a curved spatula to ensure positive adhesion to sidewalls.",
                    "Movement Monitoring: Install two-pin mechanical caliper displacement monitoring pins to track cyclic expansion."
                ]
                equipment = [
                    "Crack-chaser diamond grooving saw",
                    "Pneumatic or manual sealant caulking gun",
                    "Curved Teflon tooling spatulas",
                    "Electronic crack displacement gauge"
                ]
                safety = "RESPIRATORY & ISOCYANATE SAFETY: Provide adequate cross-ventilation; wear organic vapor respirator (NIOSH approved) when applying primers and polyurethane sealants."
                preventive = "Inspect joint elasticity every 12 months for adhesion failure or mechanical tearing."
                summary_rec = "FLEXIBLE SEALING (ACTIVE FISSURE): Active movement detected. Rout a 10mm×10mm groove, install backer rod, and seal with elastomeric polyurethane (ASTM C920 Class 35/50). Do not use rigid epoxy as it will re-crack."

            # Subcase 5B: Hairline / Minor Shrinkage (<0.20 mm)
            elif estimated_aperture_mm < 0.20 and severity == "low":
                protocol_title = "NCHRP 244 / ACI 224R Hydrophobic Penetrating Sealer Protocol"
                standard = "ACI 224R-01 & NCHRP Report 244"
                material_spec = (
                    "100% active alkyltriethoxysilane or oligomeric siloxane penetrating liquid sealer, or high-molecular-weight methacrylate (HMWM) "
                    "crack healer/sealer complying with Caltrans Standard Special Provision. Penetration depth minimum 3mm–6mm."
                )
                actions = [
                    "Pressure Wash: Clean concrete substrate with 2000 psi clean water wash to remove road dust and surface debris; allow 48-hour dry down.",
                    "Penetrating Flood Coat: Apply penetrating silane/siloxane sealer or low-viscosity HMWM crack healer over crack zone via low-pressure roller or airless sprayer at 3.5 m²/liter.",
                    "Gravity Absorption: Allow resin to gravity-feed into hairline micro-fissures (<0.20mm) to block water absorption and deicing chemical ingress.",
                    "Broadcast Aggregate: For walking or traffic surfaces, broadcast clean silica sand (20–40 mesh) over wet resin to preserve skid resistance."
                ]
                equipment = [
                    "Low-pressure airless liquid sprayer",
                    "Heavy-duty lint-free roller",
                    "Pressure washer (2000 psi)"
                ]
                safety = "VAPOR HAZARD: Highly volatile penetrating silanes produce flammable vapors. Extinguish all open flames and pilot lights."
                preventive = "Conduct water droplet absorption test after 3 years to verify hydrophobicity."
                summary_rec = "SURFACE IMPREGNATION: Hairline non-structural shrinkage. Apply deep-penetrating silane/siloxane water repellent (NCHRP 244 / ACI 224R) to prevent environmental water and chloride ingress."

            # Subcase 5C: Structural Flexural / Shear Fissure in Dry RC (ASTM C881 Epoxy Injection)
            else:
                protocol_title = "ASTM C881 Type IV Low-Viscosity Structural Epoxy Pressure Injection Protocol"
                standard = "ASTM C881 / ACI 224.1R & ACI CODE-562-25"
                material_spec = (
                    "Two-component, 100% solids, moisture-insensitive low-viscosity epoxy resin complying with ASTM C881 Type I and IV, Grade 1, Class B and C. "
                    "Compressive strength >70 MPa (ASTM D695); tensile strength >50 MPa; tensile elongation >2.0%; bond strength >14 MPa to hardened concrete. "
                    "Surface capping gel: ASTM C881 Type I Grade 3."
                )
                actions = [
                    "Surface Preparation: Clean concrete surface 50mm on either side of fissure with wire wheel or light abrasive blast to remove laitance, coatings, and efflorescence; blow crack clean with oil-free compressed air.",
                    "Port Placement: Adhere injection entry ports directly over crack centerline using fast-curing epoxy paste (ASTM C881 Type I Grade 3). Port spacing equal to member thickness (typically 150mm–300mm).",
                    "Surface Cap Seal: Apply structural epoxy capping paste (minimum 3mm thick by 50mm wide) along entire surface of crack to contain injection pressure.",
                    "Pressure Injection: Inject low-viscosity epoxy resin (ASTM C881 Type IV Grade 1) starting at lowest port under controlled pressure (0.15–0.35 MPa / 20–50 psi) until resin purges bubble-free from next port above. Cap lower port and progress upward.",
                    "Curing & Cap Removal: Allow epoxy to achieve full chemical cure (min 24–48 hours at 20°C); remove surface capping paste flush with grinder if architectural finish is required.",
                    "Forensic Verification: Extract core sample (ASTM C42) or conduct Ultrasonic Pulse Velocity (UPV) cross-hole scan to verify >90% resin penetration depth."
                ]
                equipment = [
                    "Positive-displacement 2-component epoxy injection proportioning pump",
                    "Surface injection ports and quick-connect couplers",
                    "Angle grinder with diamond cup wheel",
                    "Ultrasonic Pulse Velocity (UPV) tester"
                ]
                safety = "CHEMICAL RESIN SAFETY: Wear chemical-resistant nitrile gloves, safety goggles, and organic vapor mask. Exothermic reaction hazard if large batches are mixed."
                preventive = "Monitor tell-tale gauges and schedule periodic non-destructive acoustic pulse velocity checks."

                if is_primary and (severity == "high" or near_support):
                    actions.insert(0, "CRITICAL STRUCTURAL SHORING: Pre-load temporary hydraulic structural shoring props to support dead and construction loads prior to mechanical injection.")
                    actions.append("CFRP Shear Strengthening: For shear distress near column supports, apply externally bonded Carbon Fiber Reinforced Polymer (CFRP) composite shear wrap complying with ACI 440.2R.")
                    summary_rec = "STRUCTURAL RESTORATION & SHORING: Install temporary structural shoring. Execute low-viscosity epoxy pressure injection complying with ASTM C881 Type IV Grade 1 (ACI 224.1R). For shear fissures near supports, evaluate externally bonded CFRP composite wrap under ACI 440.2R."
                else:
                    summary_rec = "STRUCTURAL RESIN INJECTION: Clean fissure, set surface ports, and execute structural epoxy pressure injection complying with ASTM C881 Type IV Grade 1 under ACI 224.1R to restore monolithic concrete shear transfer."

        if visible_spalling or visible_corrosion:
            actions.append("Corrosion Remediation: Break out delaminated concrete to 20mm behind corroded rebar (ICRI 310.1R), blast clean steel to Sa 2.5, coat with zinc-rich primer (ASTM A898), and patch with polymer-modified repair mortar (EN 1504-3 Class R4).")

        if is_early_age:
            actions.append("Early-Age Construction Audit: Audit contractor QA records, 28-day concrete cylinder strength logs, formwork stripping records (IS 456 Cl. 11 / ACI 347), and check foundation levels for differential settlement.")

        return {
            "protocol_title": protocol_title,
            "governing_standard": standard,
            "structural_material": mat_category,
            "material_specification": material_spec,
            "prescribed_actions": actions,
            "equipment_required": equipment,
            "safety_protocol": safety,
            "preventive_maintenance": preventive,
            "summary_recommendation": summary_rec
        }

    def _build_empty_assessment(
        self,
        member_type: Optional[str] = None,
        crack_depth_status: Optional[str] = "unknown",
        standard_code: Optional[str] = "ACI",
        building_profile: Optional[Dict[str, Any]] = None,
        inspection_year: Optional[int] = None,
        calculated_age: Optional[float] = None,
        age_status_verification: str = "unknown",
        is_invalid_future_year: bool = False
    ) -> Dict[str, Any]:
        from datetime import datetime
        standard_key = (standard_code or "ACI").upper()
        if standard_key not in self.STANDARDS_LIMITS:
            standard_key = "ACI"
        std_info = self.STANDARDS_LIMITS[standard_key]

        b_profile = building_profile or {
            "building_name": None,
            "building_type": "residential",
            "construction_year": None,
            "age_years": calculated_age,
            "building_age_years": int(calculated_age) if calculated_age is not None else None,
            "age_verification": age_status_verification,
            "inspection_date": datetime.now().strftime("%Y-%m-%d"),
            "structural_system": "unknown",
            "structural_material": "reinforced_concrete",
            "structural_member": member_type or "wall",
            "member_importance": "primary",
            "repair_history": None,
            "last_major_inspection_date": None,
            "last_repair_date": None,
            "previous_crack_repairs": "unknown",
            "previous_water_leakage": False,
            "known_reinforcement_corrosion": False,
            "known_spalling_delamination": False,
            "known_settlement": False,
            "damaging_events": "none",
            "maintenance_condition": "unknown",
            "environmental_exposure": "unknown"
        }

        age_context = {
            "status": "context_documented" if calculated_age is not None else "insufficient_historical_information",
            "status_label": "Context Documented (Surface Intact)" if calculated_age is not None else "Insufficient Historical Information",
            "construction_year": b_profile.get("construction_year"),
            "inspection_year": inspection_year or datetime.now().year,
            "age_at_inspection_years": calculated_age,
            "age_verification": age_status_verification,
            "environmental_exposure": b_profile.get("environmental_exposure", "unknown"),
            "maintenance_condition": b_profile.get("maintenance_condition", "unknown"),
            "observed_deterioration_indicators": [],
            "missing_historical_information": [] if calculated_age is not None else ["Unverified construction age"],
            "age_influence_summary": "Surface scan revealed zero crack anomalies. Building age is recorded for baseline asset inventory.",
            "engineering_rationale": "No crack discontinuities detected. Intact surface condition confirmed under optical resolution.",
            "standards_consulted": [
                {
                    "standard": "ACI CODE-562-25",
                    "title": "Assessment, Repair, and Rehabilitation of Existing Concrete Structures",
                    "scope": "Condition survey baseline",
                    "verification_status": "Verified Surface Baseline"
                }
            ],
            "disclaimer": "Building age is contextual information and is not, by itself, a measure of structural safety or crack severity."
        }

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
            "building_profile": b_profile,
            "age_deterioration_context": age_context,
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
                "standard_code": standard_key,
                "building_age_years": calculated_age
            },
            "remediation_specification": {
                "protocol_title": "Routine Baseline Asset Monitoring & Preventive Seal Inspection",
                "governing_standard": f"{std_info['name']} / Preventive Asset Maintenance",
                "structural_material": str(b_profile.get("structural_material") or "reinforced_concrete"),
                "material_specification": "No active crack injection or repair material required. Maintain baseline surface coatings and elastomeric joint seals.",
                "prescribed_actions": [
                    "Record optical baseline scans in asset maintenance registry.",
                    "Verify surface drainage and joint flashings to prevent localized water accumulation.",
                    "Schedule routine visual reinspection per asset maintenance manual (annual or biennial)."
                ],
                "equipment_required": ["Digital optical inspection camera / tablet", "Visual asset inspection log"],
                "safety_protocol": "Standard site PPE (hard hat, safety footwear, high-visibility vest).",
                "preventive_maintenance": "Re-inspect surface during next scheduled periodic maintenance audit."
            },
            "unsupported_claims_disclaimer": "Surface condition appears consistent with selected criteria, but overall structural safety cannot be established from image analysis alone."
        }


morphometry_service = MorphometryService()


def calculate_building_age(construction_year: Optional[int], inspection_date: Optional[str] = None) -> Optional[int]:
    """
    Calculate building age in years using construction year and inspection date.
    Uses inspection date for historical inspections (not today's date).
    Flags/returns None for invalid future construction years or unknown year.
    """
    if construction_year is None:
        return None
    from datetime import datetime
    inspection_year = datetime.now().year
    if inspection_date:
        try:
            insp_str = str(inspection_date).strip()
            if "-" in insp_str:
                inspection_year = int(insp_str.split("-")[0])
            else:
                inspection_year = int(insp_str[:4])
        except Exception:
            inspection_year = datetime.now().year
    if construction_year > inspection_year:
        return None
    return max(0, inspection_year - construction_year)


def synthesize_age_deterioration_context(
    construction_year: Optional[int] = None,
    building_age_years: Optional[float] = None,
    age_verification: Optional[str] = "unknown",
    inspection_date: Optional[str] = None,
    environmental_exposure: Optional[str] = None,
    maintenance_condition: Optional[str] = "unknown",
    visible_spalling: bool = False,
    visible_corrosion: bool = False,
    water_leakage: bool = False,
    known_settlement: bool = False,
    damaging_events: Optional[str] = "none",
    previous_crack_repairs: Optional[str] = "unknown",
    historical_progression: Optional[str] = None,
    crack_severity: Optional[str] = None,
    crack_width_mm: Optional[float] = None
) -> Dict[str, Any]:
    from datetime import datetime
    inspection_year = datetime.now().year
    if inspection_date:
        try:
            insp_str = str(inspection_date).strip()
            if "-" in insp_str:
                inspection_year = int(insp_str.split("-")[0])
            else:
                inspection_year = int(insp_str[:4])
        except Exception:
            inspection_year = datetime.now().year

    is_invalid_future = False
    calculated_age: Optional[float] = None
    age_status_verification = age_verification or "unknown"

    if construction_year is not None:
        if construction_year > inspection_year:
            is_invalid_future = True
            calculated_age = None
            age_status_verification = "invalid_future_year"
        else:
            calculated_age = float(inspection_year - construction_year)
            if age_status_verification in ["unknown", ""]:
                age_status_verification = "documented"
    elif building_age_years is not None and building_age_years >= 0:
        calculated_age = float(building_age_years)
        if age_status_verification in ["unknown", ""]:
            age_status_verification = "estimated"

    observed_indicators = []
    if visible_spalling:
        observed_indicators.append("visible_spalling")
    if visible_corrosion:
        observed_indicators.append("visible_reinforcement_corrosion")
    if water_leakage or (environmental_exposure and "moisture" in environmental_exposure.lower()):
        observed_indicators.append("persistent_moisture_or_leakage")
    if known_settlement:
        observed_indicators.append("known_settlement_or_movement")
    if damaging_events and damaging_events != "none":
        observed_indicators.append(f"event_{damaging_events}")

    missing_info = []
    if is_invalid_future:
        missing_info.append("Construction year is in the future relative to inspection date")
    elif calculated_age is None:
        missing_info.append("Construction year and baseline age not verified")
    if maintenance_condition in ["unknown", None]:
        missing_info.append("Historical maintenance and repair log unverified")
    if previous_crack_repairs in ["unknown", None]:
        missing_info.append("Previous crack injection / sealing history unrecorded")

    is_early_age = (calculated_age is not None and calculated_age <= 5.0)

    if is_invalid_future:
        ctx_status = "insufficient_historical_information"
    elif is_early_age and (crack_severity in ["medium", "high"] or (crack_width_mm is not None and crack_width_mm >= 0.30) or len(observed_indicators) > 0 or known_settlement):
        ctx_status = "early_age_construction_defect_suspected"
    elif len(observed_indicators) >= 2 or (calculated_age is not None and calculated_age >= 25 and len(observed_indicators) >= 1):
        ctx_status = "further_deterioration_assessment_recommended" if len(observed_indicators) >= 2 else "potential_age_related_distress"
    elif calculated_age is not None:
        ctx_status = "context_documented"
    elif not observed_indicators:
        ctx_status = "insufficient_historical_information"
    else:
        ctx_status = "no_age_specific_conclusion_supported"

    reasoning_parts = []
    if calculated_age is not None:
        reasoning_parts.append(f"Building age at inspection is estimated at {int(calculated_age)} years ({age_status_verification}).")
    else:
        reasoning_parts.append("Building age is unverified.")

    if ctx_status == "early_age_construction_defect_suspected":
        reasoning_parts.append(
            f"Structure is in early service life ({int(calculated_age)} years). Under ACI 224.1R-07 and ACI CODE-562-25 Section 6.2, "
            "elevated crack width or distress in a newly constructed element cannot be attributed to normal lifecycle weathering. "
            "This condition strongly indicates construction-phase anomalies (premature formwork de-shoring, inadequate curing, "
            "construction overloading, or differential foundation settlement). Audit of contractor QA records and 28-day concrete strength logs is recommended."
        )
    elif observed_indicators:
        reasoning_parts.append(
            f"Observed or reported distress indicators ({', '.join(observed_indicators)}) "
            f"warrant focused durability and material investigation under ACI CODE-562-25 / IS 15988:2013."
        )
    else:
        reasoning_parts.append(
            "No active spalling, corrosion rust, or leakage was recorded; surface condition shows no evident age-accelerated breakdown."
        )

    reasoning_parts.append(
        "Building age provides environmental exposure context but does not independently establish structural capacity or crack severity."
    )

    return {
        "status": ctx_status,
        "construction_year": construction_year,
        "age_at_inspection": int(calculated_age) if calculated_age is not None else None,
        "age_verification": age_status_verification,
        "inspection_date": inspection_date or datetime.now().strftime("%Y-%m-%d"),
        "environmental_exposure": environmental_exposure or "unknown",
        "maintenance_condition": maintenance_condition or "unknown",
        "observed_deterioration_indicators": observed_indicators,
        "historical_progression": historical_progression or "Baseline survey",
        "missing_information": missing_info,
        "engineering_reasoning": " ".join(reasoning_parts),
        "context_disclaimer": "Building age is contextual information and is not, by itself, a measure of structural safety or crack severity."
    }


def synthesize_civil_assessment(
    crack_width_mm: float,
    crack_length_mm: float = 100.0,
    crack_count: int = 1,
    member_type: Optional[str] = "wall",
    criticality: Optional[str] = "primary",
    proximity: Optional[str] = "unspecified",
    visible_spalling: bool = False,
    visible_corrosion: bool = False,
    crack_depth_status: Optional[str] = "unknown",
    standard_code: Optional[str] = "ACI",
    construction_year: Optional[int] = None,
    inspection_date: Optional[str] = None,
    maintenance_condition: Optional[str] = "regular",
    environmental_exposure: Optional[str] = "indoor_dry",
    **kwargs
) -> Dict[str, Any]:
    scale = 0.234
    w_px = max(1.0, crack_width_mm / scale)
    l_px = max(10.0, crack_length_mm / scale)
    simulated_polygon = [
        [[100.0, 100.0], [100.0 + l_px, 100.0], [100.0 + l_px, 100.0 + w_px], [100.0, 100.0 + w_px]]
    ]
    simulated_box = [[100.0, 100.0, 100.0 + l_px, 100.0 + w_px]]

    return morphometry_service.analyze_multi_factor_condition(
        polygons=simulated_polygon,
        bounding_boxes=simulated_box,
        image_width=1000,
        image_height=1000,
        assumed_field_width_m=scale,
        member_type=member_type,
        element_criticality=criticality,
        proximity_to_supports=proximity,
        visible_spalling=visible_spalling,
        visible_corrosion=visible_corrosion,
        crack_depth_status=crack_depth_status,
        standard_code=standard_code,
        construction_year=construction_year,
        inspection_date=inspection_date,
        maintenance_condition=maintenance_condition,
        environmental_exposure=environmental_exposure,
        **kwargs
    )


def evaluate_standards_compliance(
    crack_width_mm: float,
    member_type: Optional[str] = None,
    standard_code: str = "ACI",
    environment: Optional[str] = None
) -> Dict[str, Any]:
    std_code = (standard_code or "ACI").upper()
    limits = MorphometryService.STANDARDS_LIMITS.get(std_code, MorphometryService.STANDARDS_LIMITS["ACI"])
    env_str = str(environment or "indoor_dry").lower()
    if "water" in env_str:
        limit = limits["water_retaining"]
        crit_name = "Water-Retaining Structure Limit"
    elif "marine" in env_str or "salt" in env_str or "deicing" in env_str:
        limit = limits["deicing_marine"]
        crit_name = "Deicing Chemicals & Seawater Spray Limit"
    elif "moist" in env_str or "humid" in env_str or "soil" in env_str:
        limit = limits["humidity_soil"]
        crit_name = "Humidity, Moist Air, Soil Contact Limit"
    else:
        limit = limits["dry_air_protected"]
        crit_name = "Dry Air or Protective Membrane Limit"

    within = crack_width_mm <= limit
    status = "provisionally_consistent" if within else "potential_non_conformance"

    return {
        "status": status,
        "standard_code": std_code,
        "standard_name": limits["name"],
        "standard_category": "current_standard",
        "relevant_criterion": f"{crit_name} ({limit:.2f} mm)",
        "observed_value": f"{crack_width_mm:.2f} mm",
        "reference_value": f"{limit:.2f} mm maximum permissible surface aperture",
        "explanation": f"Observed surface crack width ({crack_width_mm:.2f} mm) is {'within' if within else 'exceeds'} {limits['name']} threshold of {limit:.2f} mm.",
        "missing_information": "Overall structural compliance requires structural capacity calculation, reinforcement detailing check, and physical PE/SE verification."
    }


def audit_evidence_sufficiency(
    calibrated: bool = False,
    depth_status: str = "unknown",
    has_history: bool = False,
    spalling_checked: bool = False,
    corrosion_checked: bool = False
) -> Dict[str, Any]:
    missing = []
    if not calibrated:
        missing.append("Spatial optical scale / fiducial datum")
    if depth_status in ["unknown", "surface_only", "not_assessed"]:
        missing.append("Internal crack depth / non-destructive testing (UPV/IE)")
    if not has_history:
        missing.append("Historical progression / prior aperture readings")

    status = "sufficient_for_surface_assessment" if calibrated and spalling_checked and corrosion_checked else "insufficient_for_engineering_assessment"
    return {
        "status": status,
        "missing_factors": missing,
        "summary": "Surface photographic data provides preliminary 2D aperture metrics. Comprehensive structural assessment requires multi-factor physical testing."
    }
