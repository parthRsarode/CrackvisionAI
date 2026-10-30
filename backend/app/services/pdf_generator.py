import io
import base64
import os
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable
)
from PIL import Image as PILImage

class PDFReportGenerator:
    """
    Civil Engineering Structural Condition Assessment Report (SCAR) PDF Generator.
    Produces formal engineering audit documentation complying with DOT and municipal standards.
    """

    NAVY = colors.HexColor("#0f1f38")
    SAFETY_ORANGE = colors.HexColor("#ea580c")
    SLATE_LIGHT = colors.HexColor("#f8fafc")
    SLATE_BORDER = colors.HexColor("#cbd5e1")
    SLATE_DARK = colors.HexColor("#1e293b")
    GREEN_LIMIT = colors.HexColor("#15803d")
    RED_EXCEED = colors.HexColor("#b91c1c")

    @classmethod
    def generate_scar_pdf(cls, survey_data: Dict[str, Any], image_bytes: Optional[bytes] = None) -> bytes:
        """
        Generate a complete SCAR PDF report from survey dictionary and optional image bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Typography
        style_title = ParagraphStyle(
            'SCARTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=18,
            textColor=cls.NAVY,
            spaceAfter=2
        )
        style_subtitle = ParagraphStyle(
            'SCARSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#475569")
        )
        style_section = ParagraphStyle(
            'SCARSection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=13,
            textColor=cls.NAVY,
            spaceBefore=8,
            spaceAfter=4
        )
        style_body = ParagraphStyle(
            'SCARBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=cls.SLATE_DARK
        )
        style_body_bold = ParagraphStyle(
            'SCARBodyBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            textColor=cls.NAVY
        )
        style_callout = ParagraphStyle(
            'SCARCallout',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#334155")
        )

        elements = []

        # 1. Header Banner Table
        survey_id = survey_data.get("survey_id") or survey_data.get("analysis_id", "SCAR-000")
        created_at_str = survey_data.get("created_at") or datetime.now().isoformat()
        try:
            date_formatted = datetime.fromisoformat(created_at_str).strftime("%B %d, %Y - %H:%M UTC")
        except Exception:
            date_formatted = str(created_at_str)

        severity = str(survey_data.get("severity", "low")).upper()
        severity_color = cls.RED_EXCEED if severity == "HIGH" else (cls.SAFETY_ORANGE if severity == "MEDIUM" else cls.GREEN_LIMIT)

        header_table = Table(
            [
                [
                    Paragraph("CRACKVISION AI • INFRASTRUCTURE INSPECTION TERMINAL", style_subtitle),
                    Paragraph(f"AUDIT SPEC: {survey_data.get('standard_code', 'ACI')} 224R", style_subtitle)
                ],
                [
                    Paragraph("STRUCTURAL CONDITION ASSESSMENT REPORT (SCAR)", style_title),
                    Paragraph(f"<b>SEVERITY: {severity}</b>", ParagraphStyle('Sev', parent=style_title, fontSize=13, textColor=severity_color, alignment=2))
                ],
                [
                    Paragraph(f"Report Ref ID: <b>{survey_id}</b> | Inspection Date: {date_formatted}", style_body),
                    Paragraph(f"Status: <b>{survey_data.get('status', 'crack_detected').replace('_', ' ').upper()}</b>", style_body)
                ]
            ],
            colWidths=[380, 160]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=1.5, color=cls.NAVY, spaceBefore=4, spaceAfter=8))

        # 2. Executive Assessment Summary Table
        asset_name = survey_data.get("asset_name") or "Field Asset Component"
        metrics = survey_data.get("multi_factor_metrics") or {}
        calibration = survey_data.get("calibration") or {}

        summary_data = [
            [
                Paragraph("<b>Asset / Element:</b>", style_body),
                Paragraph(str(metrics.get("member_type") or asset_name), style_body),
                Paragraph("<b>Crack Type:</b>", style_body),
                Paragraph(str(survey_data.get("crack_type", "Fissure")), style_body_bold)
            ],
            [
                Paragraph("<b>Estimated Aperture:</b>", style_body),
                Paragraph(f"<font color='#ea580c'><b>{survey_data.get('estimated_width', '0.0 mm')}</b></font>", style_body),
                Paragraph("<b>Affected Area:</b>", style_body),
                Paragraph(str(survey_data.get("affected_area", "0.0%")), style_body)
            ],
            [
                Paragraph("<b>Scale Resolution:</b>", style_body),
                Paragraph(f"{calibration.get('mm_per_pixel', 0.234):.3f} mm/px", style_body),
                Paragraph("<b>Calibration Datum:</b>", style_body),
                Paragraph(str(calibration.get("method", "default_macro")).replace("_", " ").upper(), style_body)
            ],
            [
                Paragraph("<b>Depth Status:</b>", style_body),
                Paragraph(str(survey_data.get("crack_depth_status", "surface_only")).replace("_", " ").title(), style_body),
                Paragraph("<b>Model Confidence:</b>", style_body),
                Paragraph(f"{float(survey_data.get('confidence', 0.0)):.1f}%", style_body)
            ]
        ]
        sum_table = Table(summary_data, colWidths=[110, 160, 110, 160])
        sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cls.SLATE_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.75, cls.SLATE_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, cls.SLATE_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(sum_table)
        elements.append(Spacer(1, 6))

        # 2b. Building & Asset Profile Table
        bp = survey_data.get("building_profile") or {}
        if isinstance(bp, str):
            import json
            try:
                bp = json.loads(bp)
            except Exception:
                bp = {}

        age_ctx = survey_data.get("age_deterioration_context") or {}
        if isinstance(age_ctx, str):
            import json
            try:
                age_ctx = json.loads(age_ctx)
            except Exception:
                age_ctx = {}

        MATERIAL_LABELS = {
            "asphalt": "Asphalt / Bitumen (Road Pavement / Tar)",
            "bitumen": "Asphalt / Bitumen (Road Pavement / Tar)",
            "asphalt_concrete": "Asphalt / Bitumen (Road Pavement / Tar)",
            "reinforced_concrete": "Reinforced Concrete (Cement with Steel Rebar)",
            "prestressed_concrete": "Prestressed / Post-Tensioned Concrete (High-Tension Steel Cables)",
            "masonry": "Brickwork / Stone Masonry (Clay Bricks & Mortar)",
            "stone": "Stone Masonry / Natural Rock Wall",
            "steel": "Structural Steel (Beams / Metal Trusses)",
            "mixed_system": "Composite / Mixed Material (Concrete + Steel + Masonry)",
            "unknown": "Unknown / Unspecified Material"
        }
        ASSET_TYPE_LABELS = {
            "residential": "Residential Building (House / Apartment / Villa)",
            "commercial": "Commercial (Office / Mall / Retail / Hotel)",
            "industrial": "Industrial (Factory / Warehouse / Plant)",
            "institutional": "Institutional (School / College / Hospital)",
            "parking_structure": "Parking Structure (Multi-level Garage / Car Park)",
            "bridge": "Bridge / Flyover (Highway / Overpass / Rail)",
            "road": "Road / Highway Pavement (Street / Driveway / Runway)",
            "culvert_tunnel": "Culvert / Tunnel / Underground Passage",
            "water_retaining": "Water Tank / Swimming Pool / Reservoir / Dam",
            "retaining_wall": "Retaining Wall (Earth Support / Soil Bank)",
            "other": "Other Infrastructure"
        }

        b_name = bp.get("building_name") or survey_data.get("asset_name") or "Unnamed Structure"
        raw_b_type = str(bp.get("building_type", "unspecified")).lower()
        b_type = ASSET_TYPE_LABELS.get(raw_b_type, raw_b_type.replace("_", " ").title())
        c_year = bp.get("construction_year")
        c_year_str = str(c_year) if c_year is not None else "Unknown"
        age_val = bp.get("building_age_years")
        age_str = f"{age_val} yrs" if age_val is not None else "Unknown"
        age_ver = str(bp.get("age_verification", "unknown")).replace("_", " ").title()
        raw_mat = str(bp.get("structural_material", "reinforced_concrete")).lower()
        mat_str = MATERIAL_LABELS.get(raw_mat, raw_mat.replace("_", " ").title())
        sys_str = str(bp.get("structural_system", "unknown")).replace("_", " ").title()
        insp_date_str = str(bp.get("inspection_date") or created_at_str[:10])

        elements.append(Paragraph("<b>BUILDING & ASSET PROFILE</b>", style_section))
        b_profile_data = [
            [
                Paragraph("<b>Structure ID / Name:</b>", style_body),
                Paragraph(b_name, style_body_bold),
                Paragraph("<b>Building Type:</b>", style_body),
                Paragraph(b_type, style_body)
            ],
            [
                Paragraph("<b>Construction Year:</b>", style_body),
                Paragraph(c_year_str, style_body),
                Paragraph("<b>Age at Inspection:</b>", style_body),
                Paragraph(f"<b>{age_str}</b> ({age_ver})", style_body)
            ],
            [
                Paragraph("<b>Structural Material:</b>", style_body),
                Paragraph(mat_str, style_body),
                Paragraph("<b>Structural System:</b>", style_body),
                Paragraph(sys_str, style_body)
            ],
            [
                Paragraph("<b>Inspection Date:</b>", style_body),
                Paragraph(insp_date_str, style_body),
                Paragraph("<b>Member Importance:</b>", style_body),
                Paragraph(str(bp.get("member_importance", "primary")).title(), style_body)
            ]
        ]
        b_table = Table(b_profile_data, colWidths=[120, 150, 120, 150])
        b_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cls.SLATE_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.75, cls.SLATE_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, cls.SLATE_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(b_table)
        elements.append(Spacer(1, 6))

        # 2c. Age & Deterioration Context
        ctx_status = age_ctx.get("status", "context_documented").replace("_", " ").title()
        ctx_reason = age_ctx.get("engineering_reasoning") or (
            "Building age provides environmental and durability context but does not independently establish severity. "
            "Crack geometry, structural member type, and physical deterioration indicators govern condition assessment."
        )
        indicators = age_ctx.get("observed_deterioration_indicators") or []
        ind_str = ", ".join([str(i).replace("_", " ").title() for i in indicators]) if indicators else "None reported/visible"
        exposure_val = str(bp.get("environmental_exposure", "indoor_dry")).replace("_", " ").title()
        maint_val = str(bp.get("maintenance_condition", "regular")).replace("_", " ").title()

        elements.append(Paragraph("<b>AGE & DETERIORATION CONTEXT</b>", style_section))
        ctx_table_data = [
            [
                Paragraph("<b>Context Evaluation:</b>", style_body),
                Paragraph(f"<b>{ctx_status}</b>", style_body_bold),
                Paragraph("<b>Environmental Exposure:</b>", style_body),
                Paragraph(exposure_val, style_body)
            ],
            [
                Paragraph("<b>Observed Distress:</b>", style_body),
                Paragraph(ind_str, style_body),
                Paragraph("<b>Maintenance State:</b>", style_body),
                Paragraph(maint_val, style_body)
            ],
            [
                Paragraph("<b>Deterioration Rationale:</b>", style_body),
                Paragraph(ctx_reason, style_body),
                Paragraph("<b>Historical Progression:</b>", style_body),
                Paragraph(str(age_ctx.get("historical_progression", "Baseline reading")), style_body)
            ]
        ]
        ctx_table = Table(ctx_table_data, colWidths=[120, 150, 120, 150])
        ctx_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#94a3b8")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(ctx_table)
        elements.append(Spacer(1, 4))

        if age_ctx.get("status") == "early_age_construction_defect_suspected":
            alert_style = ParagraphStyle(
                'EarlyAgeDefectAlert',
                parent=style_callout,
                backColor=colors.HexColor("#fff1f2"),
                borderColor=colors.HexColor("#e11d48"),
                textColor=colors.HexColor("#9f1239")
            )
            elements.append(Paragraph(
                "<b>CRITICAL FORENSIC NOTICE — SUSPECTED EARLY-AGE CONSTRUCTION DEFECT (ACI 224.1R-07 & ACI CODE-562-25):</b><br/>"
                "In a structure under 5 years old, significant crack apertures in primary structural elements cannot be attributed to normal long-term environmental degradation or carbonation. "
                "Immediate forensic audit of construction-phase records is mandated: "
                "(1) Verify 28-day cylinder/cube compressive strength tests (f'ck), "
                "(2) Audit formwork stripping and de-shoring dates against IS 456 Cl. 11 / ACI 347, "
                "(3) Inspect foundation elevations for differential subsoil settlement, "
                "(4) Check curing duration and plastic/thermal shrinkage restraint logs.",
                alert_style
            ))
            elements.append(Spacer(1, 4))

        disclaimer_note = age_ctx.get("context_disclaimer") or (
            "Building age is contextual information and is not, by itself, a measure of structural safety or crack severity."
        )
        elements.append(Paragraph(f"<i><b>Engineering Note:</b> {disclaimer_note}</i>", style_callout))
        elements.append(Spacer(1, 6))

        # 3. Optional Embedded Image
        if image_bytes:
            try:
                pil_img = PILImage.open(io.BytesIO(image_bytes))
                orig_w, orig_h = pil_img.size
                max_w = 400.0
                max_h = 160.0
                ratio = min(max_w / orig_w, max_h / orig_h)
                img_w = orig_w * ratio
                img_h = orig_h * ratio

                rl_img = RLImage(io.BytesIO(image_bytes), width=img_w, height=img_h)
                elements.append(Paragraph("<b>SURFACE DAMAGE SCAN & DELINEATED DEFECT ORTHOMOSAIC</b>", style_section))
                elements.append(rl_img)
                elements.append(Spacer(1, 6))
            except Exception as e:
                pass

        # 4. Localized Digital Caliper Sampling Table (REQ-3.3)
        caliper_samples = survey_data.get("caliper_samples") or []
        elements.append(Paragraph(f"<b>LOCALIZED CALIPER SAMPLING LOG ({len(caliper_samples)} READINGS)</b>", style_section))

        if caliper_samples:
            cal_table_data = [
                [
                    Paragraph("<b>Sample ID</b>", style_body_bold),
                    Paragraph("<b>Aperture (mm)</b>", style_body_bold),
                    Paragraph("<b>Span (px)</b>", style_body_bold),
                    Paragraph("<b>Code Limit</b>", style_body_bold),
                    Paragraph("<b>Compliance Status</b>", style_body_bold),
                    Paragraph("<b>Recorded Time</b>", style_body_bold)
                ]
            ]
            std_code = survey_data.get("standard_code", "ACI")
            std_limit = 0.30 if std_code != "IS456" else 0.20

            for sample in caliper_samples[:10]:  # Up to 10 key samples
                w_mm = float(sample.get("width_mm", 0.0))
                exceeds = w_mm > std_limit
                status_p = Paragraph(
                    f"<font color='{cls.RED_EXCEED.hexval()}'><b>EXCEEDS</b></font>" if exceeds else f"<font color='{cls.GREEN_LIMIT.hexval()}'><b>WITHIN LIMIT</b></font>",
                    style_body
                )
                cal_table_data.append([
                    Paragraph(sample.get("id", "CAL"), style_body),
                    Paragraph(f"<b>{w_mm:.3f} mm</b>", style_body),
                    Paragraph(f"{float(sample.get('width_px', 0.0)):.1f} px", style_body),
                    Paragraph(f"{std_limit:.2f} mm", style_body),
                    status_p,
                    Paragraph(sample.get("timestamp", "-"), style_body)
                ])

            cal_table = Table(cal_table_data, colWidths=[70, 95, 75, 80, 110, 110])
            cal_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), cls.NAVY),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BOX', (0, 0), (-1, -1), 0.75, cls.SLATE_BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, cls.SLATE_BORDER),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(cal_table)
        else:
            elements.append(Paragraph("<i>No discrete caliper probe samples recorded. Overall continuous polygon morphometry applied.</i>", style_callout))

        elements.append(Spacer(1, 8))

        # 5. Engineering Standards & Recommendation Findings
        remed_spec = survey_data.get("remediation_specification")
        if isinstance(remed_spec, dict) and remed_spec.get("protocol_title"):
            std_title = str(remed_spec.get("governing_standard", "ENGINEERING SPECIFICATION")).upper()
            elements.append(Paragraph(f"<b>STANDARDS COMPLIANCE & REMEDIATION SPECIFICATION ({std_title})</b>", style_section))
            elements.append(Paragraph(f"<b>Prescribed Protocol:</b> {remed_spec.get('protocol_title')}", style_body_bold))
            elements.append(Paragraph(f"<b>Governing Standard:</b> {remed_spec.get('governing_standard')} &nbsp;|&nbsp; <b>Material Category:</b> {remed_spec.get('structural_material', 'Reinforced Concrete')}", style_body))
            elements.append(Paragraph(f"<b>Material Specification:</b> {remed_spec.get('material_specification')}", style_body))
            elements.append(Spacer(1, 3))

            actions = remed_spec.get("prescribed_actions", [])
            if actions:
                action_items = "<br/>".join([f"• <b>Step {i+1}:</b> {act}" for i, act in enumerate(actions)])
                elements.append(Paragraph(f"<b>Prescribed Engineering Actions:</b><br/>{action_items}", style_body))
                elements.append(Spacer(1, 3))

            equip = remed_spec.get("equipment_required", [])
            if equip:
                equip_str = ", ".join(equip)
                elements.append(Paragraph(f"<b>Required Equipment:</b> {equip_str}", style_callout))
                elements.append(Spacer(1, 2))

            if remed_spec.get("safety_protocol"):
                elements.append(Paragraph(f"<b>Safety Protocol & Hazard Controls:</b> {remed_spec.get('safety_protocol')}", style_callout))
                elements.append(Spacer(1, 2))
        else:
            elements.append(Paragraph("<b>STANDARDS COMPLIANCE & REMEDIATION PROTOCOL</b>", style_section))
            rec_text = survey_data.get("recommendation") or (
                "Monitor crack development during scheduled inspections. Clean fissure and execute remediation conforming to governing material standards."
            )
            elements.append(Paragraph(f"<b>Remediation Protocol:</b> {rec_text}", style_body))
        elements.append(Spacer(1, 4))

        disclaimer = survey_data.get("unsupported_claims_disclaimer") or (
            "DISCLAIMER: This report is an AI-assisted preliminary assessment based on surface optical imaging and does not establish overall structural capacity or replace a physical inspection by a licensed Professional Engineer (PE/SE)."
        )
        elements.append(Paragraph(f"<b>Structural Safety Advisory:</b> {disclaimer}", style_callout))
        elements.append(Spacer(1, 10))

        # 6. Official PE / SE Sign-Off Block
        signoff_data = [
            [
                Paragraph("<b>FIELD STRUCTURAL ENGINEER (PE/SE):</b>", style_body_bold),
                Paragraph("<b>DEPARTMENT AUDIT & APPROVAL:</b>", style_body_bold)
            ],
            [
                Paragraph("Signature: ___________________________________", style_body),
                Paragraph("Officer Stamp / Seal:", style_body)
            ],
            [
                Paragraph("PE License Number: ________________________", style_body),
                Paragraph("[  OFFICIAL DEPARTMENT SEAL  ]", ParagraphStyle('Seal', parent=style_body, alignment=1))
            ],
            [
                Paragraph(f"Sign-off Date: {datetime.now().strftime('%Y-%m-%d')}", style_body),
                Paragraph("Verification Status: <b>PROVISIONALLY CERTIFIED</b>", style_body)
            ]
        ]
        sign_table = Table(signoff_data, colWidths=[270, 270])
        sign_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, cls.NAVY),
            ('BACKGROUND', (0, 0), (-1, -1), cls.SLATE_LIGHT),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(sign_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = PDFReportGenerator()
