from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime


def generate_pdf_report(filename, total_rows, score, score_label, real_errors, auto_fixed):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Header ──
    title_style = ParagraphStyle(
        "title", fontSize=20, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"), spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "subtitle", fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#555555"), spaceAfter=4
    )
    label_style = ParagraphStyle(
        "label", fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#888888")
    )

    elements.append(Paragraph("SAP SuccessFactors", label_style))
    elements.append(Paragraph("Pre-Migration Data Audit Report", title_style))
    elements.append(Paragraph(f"File: {filename}", subtitle_style))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}  ·  Built by Vamsi Rayala · SAP EC Certified",
        label_style
    ))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dddddd")))
    elements.append(Spacer(1, 0.4*cm))

    # ── Score Summary ──
    if score >= 90:
        score_color = colors.HexColor("#22c55e")
    elif score >= 70:
        score_color = colors.HexColor("#f59e0b")
    elif score >= 50:
        score_color = colors.HexColor("#f97316")
    else:
        score_color = colors.HexColor("#ef4444")

    summary_data = [
        ["SAP Readiness Score", "Total Rows", "Errors Found", "Auto-Corrected"],
        [f"{score}%", str(total_rows), str(len(real_errors)), str(len(auto_fixed))]
    ]
    summary_table = Table(summary_data, colWidths=[4.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#555555")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, 1), colors.white),
        ("TEXTCOLOR", (0, 1), (0, 1), score_color),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, 1), 18),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, 1), [colors.white]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(score_label, label_style))
    elements.append(Spacer(1, 0.5*cm))

    # ── Error Table ──
    if real_errors:
        elements.append(Paragraph("Errors Requiring Manual Fix", ParagraphStyle(
            "section", fontSize=12, fontName="Helvetica-Bold",
            textColor=colors.HexColor("#1a1a2e"), spaceAfter=8
        )))

        error_data = [["Row", "Field", "Error Type", "What To Do"]]
        for e in real_errors:
            fix = e.get("What to do", e.get("description", ""))
            if len(fix) > 120:
                fix = fix[:120] + "..."
            error_data.append([
                str(e["row"]),
                str(e["field"]),
                str(e["error_type"]),
                Paragraph(fix, ParagraphStyle("cell", fontSize=7, leading=10))
            ])

        error_table = Table(error_data, colWidths=[1.5*cm, 3.5*cm, 3.5*cm, 8.5*cm])
        error_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (2, -1), 8),
            ("ALIGN", (0, 1), (2, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#eeeeee")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(error_table)
        elements.append(Spacer(1, 0.5*cm))

    # ── Auto-fixed section ──
    if auto_fixed:
        elements.append(Paragraph("Issues Auto-Corrected", ParagraphStyle(
            "section2", fontSize=12, fontName="Helvetica-Bold",
            textColor=colors.HexColor("#1a1a2e"), spaceAfter=8
        )))
        fix_data = [["Row", "Field", "Original Value", "What Was Fixed"]]
        for e in auto_fixed:
            fix_data.append([
                str(e["row"]), str(e["field"]),
                str(e["bad_value"]), str(e["description"])[:100]
            ])
        fix_table = Table(fix_data, colWidths=[1.5*cm, 3.5*cm, 4*cm, 8*cm])
        fix_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#22c55e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fdf4")]),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#eeeeee")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(fix_table)

    # ── Footer ──
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dddddd")))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "Generated by SAP EC Data Surgeon · Built by Vamsi Rayala · SAP SuccessFactors Employee Central Certified",
        ParagraphStyle("footer", fontSize=7, textColor=colors.HexColor("#aaaaaa"), alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer