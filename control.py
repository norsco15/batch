def remove_row(table, row_idx: int):
    # Suppression low-level d’une ligne de tableau (python-docx n’a pas d’API officielle)
    tbl = table._tbl
    tr = table.rows[row_idx]._tr
    tbl.remove(tr)

def trim_table_to_n_rows(table, n: int):
    # Garde uniquement les n premières lignes
    while len(table.rows) > n:
        remove_row(table, len(table.rows) - 1)


from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def fill_first_table(doc: Document, cp_ref_clean: str, title_en: str, title_fr: str):
    t = doc.tables[0]  # 1er tableau

    # ✅ Force exactement 2 lignes (supprime toute ligne “fantôme”)
    trim_table_to_n_rows(t, 2)

    # Ligne 1: header
    cell0 = t.rows[0].cells[0]
    cell0.text = cp_ref_clean
    p0 = cell0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # format du run
    if p0.runs:
        run0 = p0.runs[0]
    else:
        run0 = p0.add_run(cp_ref_clean)
    run0.bold = True
    run0.font.size = Pt(18)

    # Ligne 2: EN + saut de ligne + FR (sans créer de paragraphes supplémentaires)
    cell1 = t.rows[1].cells[0]
    cell1.text = ""  # reset
    p1 = cell1.paragraphs[0]
    r = p1.add_run(title_en)
    r.add_break()
    p1.add_run(title_fr)

    # ✅ Re-force encore après écriture (au cas où le template réinjecte une ligne)
    trim_table_to_n_rows(t, 2)
