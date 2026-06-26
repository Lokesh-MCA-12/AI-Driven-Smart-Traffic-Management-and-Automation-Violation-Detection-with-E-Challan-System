"""
PDF Challan Generator
Creates professional E-Challan PDF documents using ReportLab.
"""

import os
import logging
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.config import settings

logger = logging.getLogger(__name__)


VIOLATION_LABELS = {
    "red_light": "Red Light Violation",
    "no_helmet": "Riding without Helmet",
    "no_seatbelt": "Driving without Seatbelt",
    "overspeed": "Overspeeding",
    "wrong_lane": "Wrong Lane Driving",
}

VIOLATION_SECTIONS = {
    "red_light": "Section 119/177 - Motor Vehicles Act",
    "no_helmet": "Section 129 - Motor Vehicles Act",
    "no_seatbelt": "Section 138(3) - Motor Vehicles Act",
    "overspeed": "Section 183 - Motor Vehicles Act",
    "wrong_lane": "Section 177 - Motor Vehicles Act",
}


def generate_challan_pdf(
    challan_number: str,
    owner_name: str,
    plate_number: str,
    vehicle_type: str,
    violation_type: str,
    location: str,
    timestamp: str,
    fine_amount: float,
    due_date: str,
    evidence_image_path: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """Generate a professional E-Challan PDF document."""

    if output_dir is None:
        output_dir = os.path.join(settings.EVIDENCE_DIR, "challans")

    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{challan_number}.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=18,
        textColor=colors.HexColor("#1e3a5f"),
        spaceAfter=2,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=10,
    )

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1e3a5f"),
        spaceBefore=15,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        leading=14,
    )

    # ---- Header ----
    elements.append(Paragraph("🚦 SMART TRAFFIC MANAGEMENT AUTHORITY", title_style))
    elements.append(Paragraph("Government of India | Automated Traffic Enforcement System", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1e3a5f")))
    elements.append(Spacer(1, 15))

    # ---- E-Challan Header ----
    challan_header = Table(
        [
            [
                Paragraph(f"<b>E-CHALLAN</b>", ParagraphStyle("", fontSize=14, textColor=colors.white, alignment=TA_CENTER)),
            ]
        ],
        colWidths=[530],
    )
    challan_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1e3a5f")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
    ]))
    elements.append(challan_header)
    elements.append(Spacer(1, 15))

    # ---- Challan Details ----
    elements.append(Paragraph("CHALLAN DETAILS", header_style))

    detail_data = [
        ["Challan Number", challan_number, "Issue Date", datetime.now().strftime("%d-%m-%Y")],
        ["Vehicle Number", plate_number, "Vehicle Type", vehicle_type.title()],
        ["Owner Name", owner_name, "Due Date", due_date],
    ]

    detail_table = Table(detail_data, colWidths=[120, 145, 120, 145])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f0f4f8")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 15))

    # ---- Violation Details ----
    elements.append(Paragraph("VIOLATION INFORMATION", header_style))

    violation_data = [
        ["Violation Type", VIOLATION_LABELS.get(violation_type, violation_type)],
        ["Legal Section", VIOLATION_SECTIONS.get(violation_type, "Motor Vehicles Act")],
        ["Location", location or "N/A"],
        ["Date & Time", timestamp],
        ["Detection Method", "AI-Powered CCTV Surveillance"],
    ]

    violation_table = Table(violation_data, colWidths=[150, 380])
    violation_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(violation_table)
    elements.append(Spacer(1, 15))

    # ---- Evidence Image ----
    if evidence_image_path and os.path.exists(evidence_image_path):
        elements.append(Paragraph("EVIDENCE", header_style))
        try:
            img = Image(evidence_image_path, width=4 * inch, height=3 * inch)
            img.hAlign = "CENTER"
            elements.append(img)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(
                f"<i>Evidence captured at {timestamp}</i>",
                ParagraphStyle("", fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
            ))
            elements.append(Spacer(1, 15))
        except Exception as e:
            logger.warning(f"Could not include evidence image: {e}")

    # ---- Fine Amount ----
    fine_data = [
        [
            Paragraph(
                f"<b>FINE AMOUNT: ₹{fine_amount:.2f}</b>",
                ParagraphStyle("", fontSize=16, textColor=colors.white, alignment=TA_CENTER),
            )
        ]
    ]
    fine_table = Table(fine_data, colWidths=[530])
    fine_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e74c3c")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
    ]))
    elements.append(fine_table)
    elements.append(Spacer(1, 20))

    # ---- Instructions ----
    elements.append(Paragraph("IMPORTANT INSTRUCTIONS", header_style))
    instructions = [
        "1. Pay the fine amount within the due date to avoid additional penalties.",
        "2. Payment can be made online through the Smart Traffic portal or at authorized centers.",
        "3. If you wish to contest this challan, file a dispute within 15 days of issuance.",
        "4. Repeated violations may result in license suspension as per Motor Vehicles Act.",
        "5. This is a computer-generated document and does not require physical signature.",
    ]
    for inst in instructions:
        elements.append(Paragraph(inst, normal_style))
        elements.append(Spacer(1, 3))

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#ccc")))
    elements.append(Spacer(1, 10))

    # ---- Footer ----
    footer_style = ParagraphStyle(
        "Footer", fontSize=8, textColor=colors.grey, alignment=TA_CENTER
    )
    elements.append(Paragraph(
        "Smart Traffic Management Authority | AI-Driven Enforcement System", footer_style
    ))
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | System ID: STMS-2026",
        footer_style,
    ))

    # Build PDF
    doc.build(elements)
    logger.info(f"Challan PDF generated: {pdf_path}")
    return pdf_path
