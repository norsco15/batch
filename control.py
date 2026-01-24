import os
from docx import Document
from openpyxl import load_workbook
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

PREFIX = "F_ITG_"

def normalize_ref(ref: str) -> str:
    if ref is None:
        return ""
    ref = str(ref).strip()
    return ref[len(PREFIX):] if ref.startswith(PREFIX) else ref

def safe_name(name: str) -> str:
    bad = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for ch in bad:
        name = name.replace(ch, "_")
    return name.strip()

def get_headers(ws):
    headers = {}
    for c in range(1, ws.max_column + 1):
        v = ws.cell(row=1, column=c).value
        if v is not None:
            headers[str(v).strip()] = c
    return headers

def get_excel_value(ws, headers, row_idx: int, col_name: str) -> str:
    if col_name not in headers:
        raise ValueError(f"Colonne '{col_name}' introuvable. Dispo: {list(headers.keys())}")
    val = ws.cell(row=row_idx, column=headers[col_name]).value
    return "" if val is None else str(val)

def set_cell_lines_single_paragraph(cell, lines, *, bold=False, font_size=None, align=None):
    """
    Écrit plusieurs lignes dans UNE SEULE cellule / UN SEUL paragraphe
    (avec des retours à la ligne), pour éviter les paragraphes en plus.
    """
    cell.text = ""
    p = cell.paragraphs[0]
    if align is not None:
        p.alignment = align

    run = p.add_run(lines[0] if lines else "")
    run.bold = bold
    if font_size is not None:
        run.font.size = Pt(font_size)

    for line in lines[1:]:
        run.add_break()
        run2 = p.add_run(line)
        run2.bold = bold
        if font_size is not None:
            run2.font.size = Pt(font_size)

def fill_first_table(doc: Document, cp_ref_clean: str, title_en: str, title_fr: str):
    t = doc.tables[0]  # 1er tableau (2 lignes)

    # Ligne 1: header centré, 18, gras
    set_cell_lines_single_paragraph(
        t.rows[0].cells[0],
        [cp_ref_clean],
        bold=True,
        font_size=18,
        align=WD_ALIGN_PARAGRAPH.CENTER
    )

    # Ligne 2: 2 lignes dans la même cellule (sans créer de paragraphe)
    set_cell_lines_single_paragraph(
        t.rows[1].cells[0],
        [title_en, title_fr]
    )

def main():
    excel_path = "input.xlsx"
    sheet_name = "Sheet1"
    template_path = "template.docx"
    output_root = "output_scorecards"

    os.makedirs(output_root, exist_ok=True)

    wb = load_workbook(excel_path, data_only=True)
    ws = wb[sheet_name]
    headers = get_headers(ws)

    COL_REF = "Control Point Reference"
    COL_TITLE_EN = "Control Point Title"
    COL_TITLE_FR = "Control Point Title Loc
