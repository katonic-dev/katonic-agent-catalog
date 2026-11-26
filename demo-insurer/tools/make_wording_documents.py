"""Write the insurer's policy wordings as documents: one Markdown file and one PDF each, in ../insurance/policy-library.

The text comes from the insurer's own data, so a wording read as a document says exactly what the policy system returns.
Run from the demo-insurer folder:  python tools/make_wording_documents.py
The PDF needs the reportlab package. Without it only the Markdown files are written.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from insurer.seed_policy import WORDINGS  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "insurance" / "policy-library"
NOTICE = ("Thornmere Mutual Insurance is invented, and so is this policy wording. It is written for demonstration and is not a contract "
          "of insurance. Nothing here describes a real insurer or a real policy.")
FILES = {"TMI-MOT-01": "TMI-MOT-01-private-motor-policy-wording", "TMI-HOM-02": "TMI-HOM-02-home-buildings-and-contents-policy-wording"}


def markdown(w: dict) -> str:
    lines = [f"# {w['title']}", "", f"Thornmere Mutual Insurance (invented). Wording {w['wording_id']}, version {w['version']}.", "",
             f"> {NOTICE}", "", "## How to read this wording", "", w["how_to_read"], ""]
    section = None
    for c in w["clauses"]:
        if c["section"] != section:
            section = c["section"]
            number = c["clause"].split(".")[0]
            lines += [f"## Section {number}. {section}", ""]
        lines += [f"**{c['clause']} {c['heading']}.** {c['text']}", ""]
    return "\n".join(lines).rstrip() + "\n"


def pdf(w: dict, path: Path) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    base = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=base["BodyText"], fontSize=10.5, leading=15, spaceAfter=7)
    small = ParagraphStyle("small", parent=body, fontSize=9, leading=12, textColor="#444444")
    h1 = ParagraphStyle("h1", parent=base["Title"], fontSize=20, leading=24, alignment=0, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=base["Heading2"], fontSize=13, leading=17, spaceBefore=10, spaceAfter=6)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(20 * mm, 12 * mm, f"{w['wording_id']} version {w['version']}. Thornmere Mutual Insurance (invented). Demonstration only.")
        canvas.drawRightString(190 * mm, 12 * mm, f"Page {doc.page}")
        canvas.restoreState()

    story = [Paragraph(w["title"], h1),
             Paragraph(f"Thornmere Mutual Insurance (invented). Wording {w['wording_id']}, version {w['version']}.", body),
             Paragraph(NOTICE, small), Spacer(1, 6), Paragraph("How to read this wording", h2), Paragraph(w["how_to_read"], body)]
    section = None
    for c in w["clauses"]:
        if c["section"] != section:
            section = c["section"]
            story.append(Paragraph(f"Section {c['clause'].split('.')[0]}. {section}", h2))
        story.append(Paragraph(f"<b>{c['clause']} {c['heading']}.</b> {c['text']}", body))
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm, bottomMargin=20 * mm,
                            title=f"{w['title']} ({w['wording_id']})", author="Thornmere Mutual Insurance (invented)")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for wid, name in FILES.items():
        w = WORDINGS[wid]
        (OUT / f"{name}.md").write_text(markdown(w), encoding="utf-8", newline="\n")
        try:
            pdf(w, OUT / f"{name}.pdf")
            print("wrote", name, "as Markdown and PDF")
        except ImportError:
            print("wrote", name, "as Markdown only: the reportlab package is not installed")


if __name__ == "__main__":
    main()
