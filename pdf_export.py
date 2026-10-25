import re
from fpdf import FPDF


def _clean(text):
    """Latin-1 se bahar ke characters (emoji, fancy quotes) ko safe bana do."""
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2022": "-", "\u2026": "...",
        "\u2192": "->", "\u00a0": " ",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "ignore").decode("latin-1")


def make_pdf(report_md, sources):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    w = pdf.w - pdf.l_margin - pdf.r_margin

    for raw in report_md.split("\n"):
        line = _clean(raw.rstrip())
        line = line.replace("**", "").replace("`", "")
        pdf.set_x(pdf.l_margin)

        if not line.strip() or set(line.strip()) <= {"-"}:
            pdf.ln(3)
        elif line.startswith("# "):
            pdf.set_font("Helvetica", "B", 20)
            pdf.multi_cell(w, 10, line[2:])
            pdf.ln(2)
        elif line.startswith("## "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 15)
            pdf.multi_cell(w, 8, line[3:])
            pdf.ln(1)
        elif line.startswith("### "):
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(w, 7, line[4:])
        elif re.match(r"^\s*[\*\-] ", line):
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(w, 6, "  - " + re.sub(r"^\s*[\*\-] ", "", line))
        else:
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(w, 6, line)

    # Sources page ke end me
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 15)
    pdf.multi_cell(w, 8, "Sources")
    pdf.set_font("Helvetica", "", 10)
    for s in sources:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(w, 5, _clean(f"[{s['id']}] {s['title']}"))
        pdf.set_x(pdf.l_margin)
        pdf.set_text_color(40, 90, 200)
        pdf.multi_cell(w, 5, _clean(s["url"]))
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

    return bytes(pdf.output())