from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime

# ── Palette (light) ──
C_WHITE   = colors.white
C_BG      = colors.HexColor("#f4f6f9")
C_SURFACE = colors.white
C_BORDER  = colors.HexColor("#e2e8f0")
C_BORDER2 = colors.HexColor("#f1f5f9")
C_TEXT    = colors.HexColor("#0f172a")
C_MUTED   = colors.HexColor("#94a3b8")
C_BODY    = colors.HexColor("#475569")
C_BLUE    = colors.HexColor("#2563eb")
C_BLUE_L  = colors.HexColor("#eff6ff")
C_GREEN   = colors.HexColor("#16a34a")
C_GREEN_L = colors.HexColor("#f0fdf4")
C_AMBER   = colors.HexColor("#d97706")
C_AMBER_L = colors.HexColor("#fffbeb")
C_RED     = colors.HexColor("#dc2626")
C_RED_L   = colors.HexColor("#fff5f5")
C_ORANGE  = colors.HexColor("#ea580c")
C_HEADER_BG = colors.HexColor("#f8fafc")


def score_color(score):
    if score >= 90: return C_GREEN
    if score >= 70: return C_AMBER
    if score >= 50: return C_ORANGE
    return C_RED


def get_severity(error_type):
    t = error_type.lower()
    if "auto-fix"    in t: return "autofixed"
    if "warning"     in t: return "warning"
    if "cross-field" in t: return "info"
    return "critical"


def sev_meta(sev):
    return {
        "critical":  ("CRITICAL",  C_RED,    C_RED_L),
        "warning":   ("WARNING",   C_AMBER,  C_AMBER_L),
        "info":      ("NOTICE",    C_BLUE,   C_BLUE_L),
        "autofixed": ("AUTO-FIXED",C_GREEN,  C_GREEN_L),
    }.get(sev, ("INFO", C_MUTED, C_BORDER2))


def S():
    """Return style dictionary."""
    return {
        "eyebrow": ParagraphStyle("eyebrow", fontSize=8,
            fontName="Helvetica", textColor=C_BLUE, leading=11),
        "title": ParagraphStyle("title", fontSize=22,
            fontName="Helvetica-Bold", textColor=C_TEXT,
            leading=26, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", fontSize=10,
            fontName="Helvetica", textColor=C_BODY, leading=14),
        "meta_r": ParagraphStyle("meta_r", fontSize=8,
            fontName="Helvetica", textColor=C_MUTED,
            leading=11, alignment=TA_RIGHT),
        "meta": ParagraphStyle("meta", fontSize=8,
            fontName="Helvetica", textColor=C_MUTED, leading=11),
        "sec_head": ParagraphStyle("sec_head", fontSize=9,
            fontName="Helvetica-Bold", textColor=C_BLUE,
            leading=12, spaceBefore=16, spaceAfter=6),
        "card_label": ParagraphStyle("card_label", fontSize=8,
            fontName="Helvetica", textColor=C_MUTED,
            leading=10, alignment=TA_CENTER),
        "card_value": ParagraphStyle("card_value", fontSize=24,
            fontName="Helvetica-Bold", textColor=C_TEXT,
            leading=28, alignment=TA_CENTER),
        "card_sub": ParagraphStyle("card_sub", fontSize=8,
            fontName="Helvetica", textColor=C_MUTED,
            leading=10, alignment=TA_CENTER),
        "hdr": ParagraphStyle("hdr", fontSize=8,
            fontName="Helvetica-Bold", textColor=C_MUTED, leading=10),
        "mono": ParagraphStyle("mono", fontSize=8,
            fontName="Courier", textColor=C_BLUE, leading=11),
        "row_num": ParagraphStyle("row_num", fontSize=8,
            fontName="Courier", textColor=C_MUTED, leading=10),
        "badge": ParagraphStyle("badge", fontSize=7,
            fontName="Helvetica-Bold", textColor=C_WHITE,
            leading=9, alignment=TA_CENTER),
        "body": ParagraphStyle("body", fontSize=8,
            fontName="Helvetica", textColor=C_BODY,
            leading=12, wordWrap="CJK"),
        "footer": ParagraphStyle("footer", fontSize=7,
            fontName="Helvetica", textColor=C_MUTED,
            leading=10, alignment=TA_CENTER),
    }


def generate_pdf_report(filename, total_rows, score,
                         score_label, real_errors, auto_fixed):
    buffer = BytesIO()
    W = A4[0] - 3.6*cm

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="SAP EC Pre-Migration Audit Report",
        author="Vamsi Rayala"
    )

    st = S()
    elems = []

    # ── HEADER ──────────────────────────────────────────────────
    elems.append(Table(
        [[Paragraph("SAP SUCCESSFACTORS · EMPLOYEE CENTRAL", st["eyebrow"])]],
        colWidths=[W],
        style=[
            ("BACKGROUND",    (0,0),(-1,-1), C_BLUE),
            ("TOPPADDING",    (0,0),(-1,-1), 10),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("LEFTPADDING",   (0,0),(-1,-1), 16),
            ("RIGHTPADDING",  (0,0),(-1,-1), 16),
            ("TEXTCOLOR",     (0,0),(-1,-1), C_WHITE),
        ]
    ))
    # Override eyebrow color for dark bg
    elems[-1]._cellvalues[0][0].style.textColor = C_WHITE

    elems.append(Table(
        [[Paragraph("Pre-Migration Data Audit Report", st["title"])]],
        colWidths=[W],
        style=[
            ("BACKGROUND",    (0,0),(-1,-1), C_SURFACE),
            ("TOPPADDING",    (0,0),(-1,-1), 14),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 16),
            ("RIGHTPADDING",  (0,0),(-1,-1), 16),
        ]
    ))

    gen_date = datetime.now().strftime("%d %B %Y · %H:%M")
    elems.append(Table(
        [[Paragraph(f"File: {filename}", st["subtitle"]),
          Paragraph(f"Generated: {gen_date}", st["meta_r"])]],
        colWidths=[W*0.6, W*0.4],
        style=[
            ("BACKGROUND",    (0,0),(-1,-1), C_SURFACE),
            ("TOPPADDING",    (0,0),(-1,-1), 2),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("LEFTPADDING",   (0,0),(-1,-1), 16),
            ("RIGHTPADDING",  (0,0),(-1,-1), 16),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ]
    ))

    elems.append(Table(
        [[Paragraph(
            "Built by Vamsi Rayala · SAP SuccessFactors Employee Central Certified · "
            "sapdatavalidator.streamlit.app",
            st["meta"])]],
        colWidths=[W],
        style=[
            ("BACKGROUND",    (0,0),(-1,-1), C_HEADER_BG),
            ("LINEABOVE",     (0,0),(-1,-1), 0.5, C_BORDER),
            ("LINEBELOW",     (0,0),(-1,-1), 0.5, C_BORDER),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("LEFTPADDING",   (0,0),(-1,-1), 16),
            ("RIGHTPADDING",  (0,0),(-1,-1), 16),
        ]
    ))
    elems.append(Spacer(1, 0.5*cm))

    # ── SCORE CARDS ──────────────────────────────────────────────
    sc = score_color(score)

    def card(label, value, value_color=C_TEXT, sub=None):
        content = [
            Paragraph(label, st["card_label"]),
            Paragraph(str(value), ParagraphStyle(
                "cv2", fontSize=24, fontName="Helvetica-Bold",
                textColor=value_color, leading=28, alignment=TA_CENTER)),
        ]
        if sub:
            content.append(Paragraph(sub, st["card_sub"]))
        return content

    score_cell = [
        Paragraph("SAP READINESS SCORE", st["card_label"]),
        Paragraph(f"{score}%", ParagraphStyle(
            "sc2", fontSize=30, fontName="Helvetica-Bold",
            textColor=sc, leading=34, alignment=TA_CENTER)),
        Paragraph(score_label, st["card_sub"]),
    ]

    cw = W / 4
    elems.append(Table(
        [[score_cell,
          card("TOTAL ROWS", f"{total_rows:,}"),
          card("ERRORS FOUND", len(real_errors),
               C_RED if real_errors else C_GREEN),
          card("AUTO-CORRECTED", len(auto_fixed),
               C_GREEN if auto_fixed else C_TEXT)]],
        colWidths=[cw, cw, cw, cw],
        rowHeights=[88],
        style=[
            ("BACKGROUND",    (0,0),(-1,-1), C_SURFACE),
            ("BOX",           (0,0),(-1,-1), 0.5, C_BORDER),
            ("INNERGRID",     (0,0),(-1,-1), 0.5, C_BORDER),
            ("LINEBELOW",     (0,0),(0,-1),  3,   sc),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ("ALIGN",         (0,0),(-1,-1), "CENTER"),
            ("TOPPADDING",    (0,0),(-1,-1), 10),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("LEFTPADDING",   (0,0),(-1,-1), 6),
            ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ]
    ))
    elems.append(Spacer(1, 0.5*cm))

    # ── ERROR TABLE ───────────────────────────────────────────────
    if real_errors:
        elems.append(Paragraph(
            f"ERRORS REQUIRING MANUAL FIX  ({len(real_errors)})",
            st["sec_head"]))

        cw_row   = 0.9*cm
        cw_field = 3.0*cm
        cw_sev   = 2.0*cm
        cw_msg   = W - cw_row - cw_field - cw_sev

        rows = [[
            Paragraph("ROW",   st["hdr"]),
            Paragraph("FIELD", st["hdr"]),
            Paragraph("TYPE",  st["hdr"]),
            Paragraph("EXPLANATION & RECOMMENDED FIX", st["hdr"]),
        ]]

        tstyles = [
            ("BACKGROUND",    (0,0),(-1,0),  C_HEADER_BG),
            ("LINEBELOW",     (0,0),(-1,0),  1, C_BORDER),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ("LEFTPADDING",   (0,0),(-1,-1), 6),
            ("RIGHTPADDING",  (0,0),(-1,-1), 6),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("BOX",           (0,0),(-1,-1), 0.5, C_BORDER),
        ]

        for i, e in enumerate(real_errors):
            sev = get_severity(e.get("error_type",""))
            label, sev_c, sev_bg = sev_meta(sev)
            fix = (e.get("ai_fix") or e.get("What to do")
                   or e.get("description","")).strip()
            ri = i + 1
            row_bg = sev_bg if i % 2 == 0 else C_WHITE

            badge_tbl = Table(
                [[Paragraph(label, st["badge"])]],
                colWidths=[1.7*cm],
                style=[
                    ("BACKGROUND",    (0,0),(-1,-1), sev_c),
                    ("TOPPADDING",    (0,0),(-1,-1), 3),
                    ("BOTTOMPADDING", (0,0),(-1,-1), 3),
                    ("LEFTPADDING",   (0,0),(-1,-1), 4),
                    ("RIGHTPADDING",  (0,0),(-1,-1), 4),
                ]
            )

            rows.append([
                Paragraph(str(e.get("row","")), st["row_num"]),
                Paragraph(str(e.get("field","")), st["mono"]),
                badge_tbl,
                Paragraph(fix, st["body"]),
            ])
            tstyles += [
                ("BACKGROUND", (0,ri),(-1,ri), row_bg),
                ("LINEBELOW",  (0,ri),(-1,ri), 0.5, C_BORDER2),
                ("LINEBEFORE", (0,ri),(0, ri), 3,   sev_c),
            ]

        elems.append(Table(
            rows,
            colWidths=[cw_row, cw_field, cw_sev, cw_msg],
            repeatRows=1,
            style=tstyles
        ))
        elems.append(Spacer(1, 0.4*cm))

    # ── AUTO-FIXED TABLE ──────────────────────────────────────────
    if auto_fixed:
        elems.append(Paragraph(
            f"ISSUES AUTO-CORRECTED  ({len(auto_fixed)})",
            st["sec_head"]))

        cw_row2   = 0.9*cm
        cw_field2 = 3.0*cm
        cw_orig   = 3.2*cm
        cw_fix2   = W - cw_row2 - cw_field2 - cw_orig

        fix_rows = [[
            Paragraph("ROW",            st["hdr"]),
            Paragraph("FIELD",          st["hdr"]),
            Paragraph("ORIGINAL VALUE", st["hdr"]),
            Paragraph("WHAT WAS FIXED", st["hdr"]),
        ]]
        fstyles = [
            ("BACKGROUND",    (0,0),(-1,0),  C_HEADER_BG),
            ("LINEBELOW",     (0,0),(-1,0),  1, C_BORDER),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ("LEFTPADDING",   (0,0),(-1,-1), 6),
            ("RIGHTPADDING",  (0,0),(-1,-1), 6),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("BOX",           (0,0),(-1,-1), 0.5, C_BORDER),
        ]
        for i, e in enumerate(auto_fixed):
            ri = i + 1
            row_bg = C_GREEN_L if i % 2 == 0 else C_WHITE
            fix_rows.append([
                Paragraph(str(e.get("row","")),        st["row_num"]),
                Paragraph(str(e.get("field","")),      st["mono"]),
                Paragraph(str(e.get("bad_value","")),  st["body"]),
                Paragraph(str(e.get("description","")),st["body"]),
            ])
            fstyles += [
                ("BACKGROUND", (0,ri),(-1,ri), row_bg),
                ("LINEBELOW",  (0,ri),(-1,ri), 0.5, C_BORDER2),
                ("LINEBEFORE", (0,ri),(0, ri), 3,   C_GREEN),
            ]

        elems.append(Table(
            fix_rows,
            colWidths=[cw_row2, cw_field2, cw_orig, cw_fix2],
            repeatRows=1,
            style=fstyles
        ))

    # ── FOOTER ────────────────────────────────────────────────────
    elems.append(Spacer(1, 0.6*cm))
    elems.append(HRFlowable(
        width="100%", thickness=0.5,
        color=C_BORDER, spaceAfter=6))
    elems.append(Paragraph(
        "Generated by SAP EC Data Surgeon  ·  "
        "Built by Vamsi Rayala  ·  "
        "SAP SuccessFactors Employee Central Certified",
        st["footer"]))

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_BG)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(C_MUTED)
        canvas.drawCentredString(A4[0]/2, 0.8*cm, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(elems, onFirstPage=on_page, onLaterPages=on_page)
    buffer.seek(0)
    return buffer