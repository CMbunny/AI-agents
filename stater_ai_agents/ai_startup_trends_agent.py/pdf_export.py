import io
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER


def _strip_markdown(text: str) -> str:
    """Strip basic markdown so reportlab doesn't render asterisks/hashes as literals."""
    text = re.sub(r"#{1,6}\s*", "", text)        # headings
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # bold
    text = re.sub(r"\*(.*?)\*", r"\1", text)       # italic
    text = re.sub(r"`(.*?)`", r"\1", text)         # inline code
    text = text.replace("\\$", "$")                # escaped dollar signs
    return text.strip()


def _markdown_to_story(text: str, styles: dict) -> list:
    """
    Convert markdown text to a list of reportlab Paragraph/Spacer flowables.
    Handles: ### headings, bullet points (- ), bold (**text**), normal paragraphs.
    """
    story = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 6))
            continue

        # Headings
        if stripped.startswith("### "):
            story.append(Spacer(1, 8))
            story.append(Paragraph(_strip_markdown(stripped[4:]), styles["h3"]))
            story.append(Spacer(1, 4))
        elif stripped.startswith("## "):
            story.append(Spacer(1, 10))
            story.append(Paragraph(_strip_markdown(stripped[3:]), styles["h2"]))
            story.append(Spacer(1, 6))
        elif stripped.startswith("# "):
            story.append(Paragraph(_strip_markdown(stripped[2:]), styles["h1"]))
            story.append(Spacer(1, 8))
        # Bullets
        elif stripped.startswith("- ") or stripped.startswith("* "):
            content = _strip_markdown(stripped[2:])
            story.append(Paragraph(f"• {content}", styles["bullet"]))
            story.append(Spacer(1, 3))
        # Numbered list
        elif re.match(r"^\d+\.", stripped):
            content = _strip_markdown(re.sub(r"^\d+\.\s*", "", stripped))
            story.append(Paragraph(content, styles["bullet"]))
            story.append(Spacer(1, 3))
        # Divider
        elif stripped == "---":
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
            story.append(Spacer(1, 6))
        # Normal paragraph
        else:
            story.append(Paragraph(_strip_markdown(stripped), styles["body"]))
            story.append(Spacer(1, 4))

    return story


def generate_pdf(
    topic: str,
    timestamp: str,
    angles_used: list,
    analysis: str,
    competitors: str,
    summaries: str,
    news: str,
) -> bytes:
    """
    Generate a PDF report and return it as bytes for Streamlit download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    base_styles = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "title", parent=base_styles["Title"],
            fontSize=20, spaceAfter=6, textColor=colors.HexColor("#1a1a2e"),
        ),
        "meta": ParagraphStyle(
            "meta", parent=base_styles["Normal"],
            fontSize=9, textColor=colors.grey, spaceAfter=4,
        ),
        "section": ParagraphStyle(
            "section", parent=base_styles["Heading1"],
            fontSize=14, spaceBefore=12, spaceAfter=6,
            textColor=colors.HexColor("#1a1a2e"),
            borderPad=4,
        ),
        "h1": ParagraphStyle("h1", parent=base_styles["Heading1"], fontSize=13, spaceBefore=8),
        "h2": ParagraphStyle("h2", parent=base_styles["Heading2"], fontSize=11, spaceBefore=6),
        "h3": ParagraphStyle("h3", parent=base_styles["Heading3"], fontSize=10, spaceBefore=4),
        "body": ParagraphStyle("body", parent=base_styles["Normal"], fontSize=9, leading=14),
        "bullet": ParagraphStyle(
            "bullet", parent=base_styles["Normal"],
            fontSize=9, leading=13, leftIndent=16,
        ),
    }

    story = []

    # ── Cover / Header ────────────────────────────────────────────────────────
    story.append(Paragraph("AI Startup Trend Analysis", styles["title"]))
    story.append(Paragraph(f"Topic: {topic}", styles["meta"]))
    story.append(Paragraph(f"Generated: {timestamp}", styles["meta"]))
    story.append(Paragraph(f"Search angles: {', '.join(angles_used)}", styles["meta"]))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a1a2e")))
    story.append(Spacer(1, 12))

    # ── Trend Analysis ────────────────────────────────────────────────────────
    story.append(Paragraph("📊 Trend Analysis & Startup Opportunities", styles["section"]))
    story.append(Spacer(1, 6))
    story.extend(_markdown_to_story(analysis, styles))
    story.append(PageBreak())

    # ── Competitor Map ────────────────────────────────────────────────────────
    story.append(Paragraph("🏢 Competitor Map", styles["section"]))
    story.append(Spacer(1, 6))
    story.extend(_markdown_to_story(competitors, styles))
    story.append(PageBreak())

    # ── Article Summaries ─────────────────────────────────────────────────────
    story.append(Paragraph("📰 Article Summaries", styles["section"]))
    story.append(Spacer(1, 6))
    for line in summaries.splitlines():
        stripped = line.strip()
        if stripped:
            story.append(Paragraph(f"• {_strip_markdown(stripped)}", styles["bullet"]))
            story.append(Spacer(1, 3))
    story.append(PageBreak())

    # ── Raw News ──────────────────────────────────────────────────────────────
    story.append(Paragraph("🔗 Raw News Collection", styles["section"]))
    story.append(Spacer(1, 6))
    for line in news.splitlines():
        stripped = line.strip()
        if stripped:
            story.append(Paragraph(f"• {_strip_markdown(stripped)}", styles["bullet"]))
            story.append(Spacer(1, 3))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()