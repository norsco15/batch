import os
from docx import Document
from openpyxl import load_workbook

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

def set_cell_paragraphs(cell, lines):
    # Remplace le contenu par 1 paragraphe par ligne (retours à la ligne propres)
    cell.text = ""
    p0 = cell.paragraphs[0]
    p0.text = lines[0] if lines else ""
    for line in lines[1:]:
        cell.add_paragraph(line)

def fill_first_table(doc: Document, cp_ref: str, title_en: str, title_fr: str):
    t = doc.tables[0]  # 1er tableau (2 lignes)
    cp_ref = (cp_ref or "").strip()
    set_cell_paragraphs(t.rows[0].cells[0], [cp_ref])
    set_cell_paragraphs(t.rows[1].cells[0], [title_en, title_fr])

def safe_name(name: str) -> str:
    # Nettoyage minimal pour éviter caractères interdits Windows
    bad = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for ch in bad:
        name = name.replace(ch, "_")
    return name.strip()

def main():
    excel_path = "input.xlsx"
    sheet_name = "Sheet1"
    template_path = "template.docx"
    output_root = "output_scorecards"  # dossier racine de sortie

    os.makedirs(output_root, exist_ok=True)

    wb = load_workbook(excel_path, data_only=True)
    ws = wb[sheet_name]
    headers = get_headers(ws)

    # Colonnes Excel
    COL_REF = "Control Point Reference"                 # déjà sans "F_ITG_"
    COL_TITLE_EN = "Control Point Title"
    COL_TITLE_FR = "Control Point Title Local Language"

    # Parcours de toutes les lignes (à partir de la ligne 2)
    for row_idx in range(2, ws.max_row + 1):
        cp_ref = get_excel_value(ws, headers, row_idx, COL_REF).strip()

        # Ignore lignes vides (ou fin de fichier)
        if not cp_ref:
            continue

        title_en = get_excel_value(ws, headers, row_idx, COL_TITLE_EN)
        title_fr = get_excel_value(ws, headers, row_idx, COL_TITLE_FR)

        # Noms dossier/fichier
        ref_clean = safe_name(cp_ref)
        out_dir = os.path.join(output_root, ref_clean)
        os.makedirs(out_dir, exist_ok=True)

        out_path = os.path.join(out_dir, f"{ref_clean}.docx")

        # Génération Word
        doc = Document(template_path)
        fill_first_table(doc, cp_ref, title_en, title_fr)
        doc.save(out_path)

        print(f"Generated: {out_path}")

if __name__ == "__main__":
    main()
