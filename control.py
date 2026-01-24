import re

def norm_ws(s: str) -> str:
    """Normalise les espaces et retours ligne pour comparer."""
    s = "" if s is None else str(s)
    s = s.replace("\xa0", " ")          # nbsp
    s = s.replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def write_en_fr_in_cell(cell, en_text: str, fr_text: str):
    """
    Remplit UNE cellule avec 2 lignes (EN puis FR) sans créer de paragraphes en plus.
    """
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run(en_text or "")
    r.add_break()
    p.add_run(fr_text or "")

def find_cell_containing(doc, needle: str):
    """
    Retourne (table, r, c) de la 1ère cellule dont le texte contient needle (normalisé).
    """
    needle_n = norm_ws(needle)
    for table in doc.tables:
        for r_i, row in enumerate(table.rows):
            for c_i, cell in enumerate(row.cells):
                if needle_n in norm_ws(cell.text):
                    return table, r_i, c_i
    return None





def fill_score_table(doc, s1_en, s1_fr, s2_en, s2_fr, s3_en, s3_fr, s4_en, s4_fr):
    mapping = [
        ("Score = 1 : Control Point Satisfactory", s1_en, s1_fr),
        ("Score = 2 : Control Point Globally Satisfactory", s2_en, s2_fr),
        ("Score = 3 : Control Point Marginally Satisfactory", s3_en, s3_fr),
        ("Score = 4 : Control Point Unsatisfactory", s4_en, s4_fr),
    ]

    for header_text, en_val, fr_val in mapping:
        found = find_cell_containing(doc, header_text)
        if not found:
            raise ValueError(f"Header introuvable dans Word: '{header_text}'")

        table, r, c = found

        # On écrit dans la cellule en dessous (même colonne)
        if r + 1 >= len(table.rows):
            raise IndexError(f"Pas de ligne sous le header '{header_text}'")

        target_cell = table.rows[r + 1].cells[c]
        write_en_fr_in_cell(target_cell, en_val, fr_val)







s1_en = get_excel_value(ws, headers, row_idx, "Control Point Satisfactory")
s1_fr = get_excel_value(ws, headers, row_idx, "Control Point Satisfactory Local Language")

s2_en = get_excel_value(ws, headers, row_idx, "Control Point Globally Satisfactory")
s2_fr = get_excel_value(ws, headers, row_idx, "Control Point Globally Satisfactory Local Language")

s3_en = get_excel_value(ws, headers, row_idx, "Control Point Marginally Satisfactory")
s3_fr = get_excel_value(ws, headers, row_idx, "Control Point Marginally Satisfactory Local Language")

s4_en = get_excel_value(ws, headers, row_idx, "Control Point Unsatisfactory")
s4_fr = get_excel_value(ws, headers, row_idx, "Control Point Unsatisfactory Local Language")





fill_score_table(doc, s1_en, s1_fr, s2_en, s2_fr, s3_en, s3_fr, s4_en, s4_fr)
