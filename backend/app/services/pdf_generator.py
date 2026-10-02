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
        elements.append(Spacer(1, 8))

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
        elements.append(Paragraph("<b>STANDARDS COMPLIANCE & ASTM C881 REMEDIATION PROTOCOL</b>", style_section))
        rec_text = survey_data.get("recommendation") or (
            "Monitor crack development during scheduled inspections. Clean fissure and execute structural pressure injection with epoxy resin complying with ASTM C881 Type IV, Grade 1."
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
