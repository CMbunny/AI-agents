from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib import colors
from pathlib import Path
from datetime import datetime


# ── Color Palette ──────────────────────────────────────────────────────────
PINK        = HexColor("#E91E8C")
DARK        = HexColor("#1A1A2E")
LIGHT_GRAY  = HexColor("#F5F5F5")
MID_GRAY    = HexColor("#888888")
WHITE       = HexColor("#FFFFFF")


def _styles():
    base = getSampleStyleSheet()

    app_title = ParagraphStyle(
        "AppTitle",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=MID_GRAY,
        spaceAfter=2,
    )

    city_title = ParagraphStyle(
        "CityTitle",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=28,
        textColor=DARK,
        spaceAfter=6,
    )

    meta_label = ParagraphStyle(
        "MetaLabel",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=MID_GRAY,
        spaceAfter=2,
    )

    meta_value = ParagraphStyle(
        "MetaValue",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK,
        spaceAfter=8,
    )

    route_title = ParagraphStyle(
        "RouteTitle",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=WHITE,
        spaceAfter=4,
    )

    stop_header = ParagraphStyle(
        "StopHeader",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=PINK,
        spaceBefore=16,
        spaceAfter=6,
    )

    section_label = ParagraphStyle(
        "SectionLabel",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=MID_GRAY,
        spaceBefore=8,
        spaceAfter=2,
    )

    body = ParagraphStyle(
        "TourBody",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=11,
        textColor=DARK,
        leading=17,
        spaceAfter=8,
    )

    footer = ParagraphStyle(
        "Footer",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=MID_GRAY,
        spaceAfter=0,
    )

    return {
        "app_title": app_title,
        "city_title": city_title,
        "meta_label": meta_label,
        "meta_value": meta_value,
        "route_title": route_title,
        "stop_header": stop_header,
        "section_label": section_label,
        "body": body,
        "footer": footer,
    }


def _build_route_table(stops: list, styles: dict) -> Table:
    """Builds a styled route row: Stop 1 → Stop 2 → Stop 3"""
    arrow = "  →  "
    route_text = arrow.join(stops)

    data = [
        [Paragraph("🗺  Route", styles["route_title"])],
        [Paragraph(route_text, ParagraphStyle(
            "RouteBody",
            fontName="Helvetica",
            fontSize=10,
            textColor=WHITE,
            leading=14,
        ))]
    ]

    table = Table(data, colWidths=[17 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK),
        ("ROUNDEDCORNERS", [6]),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))
    return table


def _build_meta_table(metadata: dict, styles: dict) -> Table:
    """Builds a two-column metadata info box."""
    items = [
        ("Stops", str(len(metadata["stops"]))),
        ("Duration", f"{metadata['duration']} minutes"),
        ("Interests", ", ".join(metadata["interests"])),
        ("Language", metadata["language"]),
        ("Persona", metadata["persona"]),
        ("Est. Cost", f"${metadata['estimated_cost']:.4f} USD"),
        ("Generated", metadata["created_at"]),
    ]

    rows = []
    for i in range(0, len(items), 2):
        row = []
        for label, value in items[i:i+2]:
            cell = [
                Paragraph(label.upper(), styles["meta_label"]),
                Paragraph(value, styles["meta_value"]),
            ]
            row.append(cell)
        if len(row) == 1:
            row.append("")
        rows.append(row)

    table = Table(rows, colWidths=[8.5 * cm, 8.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, HexColor("#DDDDDD")),
    ]))
    return table


def generate_pdf(
    city: str,
    stops: list,
    interests: list,
    language: str,
    persona: str,
    duration: int,
    estimated_cost: float,
    content: str,
) -> Path:
    """
    Generates a styled PDF for the tour and returns the file path.
    Content is expected to have stop sections separated by '--- Stop Name ---' markers.
    """

    output_path = Path(__file__).parent / f"tour_{city.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    s = _styles()
    story = []
    created_at = datetime.now().strftime("%B %d, %Y at %H:%M")

    # ── App Title ──────────────────────────────────────────────────────────
    story.append(Paragraph("🎧 AI Audio Tour Agent", s["app_title"]))
    story.append(Spacer(1, 4))

    # ── City Title ─────────────────────────────────────────────────────────
    story.append(Paragraph(city, s["city_title"]))
    story.append(HRFlowable(width="100%", thickness=2, color=PINK, spaceAfter=12))

    # ── Metadata Box ───────────────────────────────────────────────────────
    story.append(_build_meta_table({
        "stops": stops,
        "duration": duration,
        "interests": interests,
        "language": language,
        "persona": persona,
        "estimated_cost": estimated_cost,
        "created_at": created_at,
    }, s))
    story.append(Spacer(1, 16))

    # ── Route Box ─────────────────────────────────────────────────────────
    story.append(_build_route_table(stops, s))
    story.append(Spacer(1, 20))

    # ── Tour Content ───────────────────────────────────────────────────────
    # Split content by stop markers
    sections = content.split("\n\n")
    current_stop = None

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Check if this is a stop header marker
        if section.startswith("---") and section.endswith("---"):
            stop_name = section.replace("---", "").strip()
            current_stop = stop_name
            story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#DDDDDD"), spaceBefore=8, spaceAfter=8))
            story.append(Paragraph(f"📍 {stop_name}", s["stop_header"]))
        else:
            story.append(Paragraph(section, s["body"]))
            story.append(Spacer(1, 4))

    # ── Footer ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#DDDDDD")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated by AI Audio Tour Agent  •  {created_at}  •  {language}  •  {persona}",
        s["footer"]
    ))

    doc.build(story)
    return output_path