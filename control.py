from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def _clear_cell_paragraphs(cell):
    # Supprime tous les paragraphes existants (important pour éviter une "ligne" fantôme)
    for p in cell.paragraphs:
        p._element.getparent().remove(p._element)
    # Recrée un paragraphe vide
    cell.add_paragraph()

def set_cell_lines_single_paragraph(cell, lines, *, bold=False, font_size=None, align=None):
    _clear_cell_paragraphs(cell)

    p = cell.paragraphs[0]

    # ✅ évite l'effet "ligne en plus" (espacement)
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1

    if align is not None:
        p.alignment = align

    if not lines:
        return

    r = p.add_run(lines[0])
    r.bold = bold
    if font_size is not None:
        r.font.size = Pt(font_size)

    for line in lines[1:]:
        r.add_break()
        r2 = p.add_run(line)
        r2.bold = bold
        if font_size is not None:
            r2.font.size = Pt(font_size)
