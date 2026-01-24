def split_by_interpoint(text: str):
    """
    Split sur le caractère interpoint '·' et nettoie.
    """
    if text is None:
        return []
    parts = [p.strip() for p in str(text).split("·")]
    return [p for p in parts if p]  # enlève vides

def find_table_and_header_row(doc, header_text: str):
    """
    Trouve le tableau qui contient une cellule dont le texte contient header_text.
    Retourne (table, header_row_index, header_col_index)
    """
    found = find_cell_containing(doc, header_text)  # ton helper existant
    if not found:
        return None
    table, r, c = found
    return table, r, c

def fill_verification_table(doc, cp_ref_clean: str, meth_en: str, meth_fr: str):
    # 1) Split EN/FR
    en_points = split_by_interpoint(meth_en)
    fr_points = split_by_interpoint(meth_fr)

    n = max(len(en_points), len(fr_points))
    if n == 0:
        return  # rien à remplir

    # 2) Trouver le tableau "Verification ID"
    res = find_table_and_header_row(doc, "Verification ID")
    if not res:
        raise ValueError("Table 'Verification ID' introuvable dans le Word.")
    table, header_r, _ = res

    # 3) Supprimer toutes les lignes sous le header (lignes fantômes / template)
    # On garde toutes les lignes jusqu’au header inclus.
    trim_table_to_row_count(table, header_r + 1)  # tu as déjà cette fonction

    # 4) Ajouter exactement n lignes
    for i in range(n):
        table.add_row()

        row_idx = header_r + 1 + i
        row = table.rows[row_idx]

        verif_id = f"{cp_ref_clean}-V{i+1}"
        row.cells[0].text = verif_id

        en_txt = en_points[i] if i < len(en_points) else ""
        fr_txt = fr_points[i] if i < len(fr_points) else ""
        write_en_fr_in_cell(row.cells[1], en_txt, fr_txt)  # ton helper existant

        # Result / Evidence laissés vides
        row.cells[2].text = ""
        row.cells[3].text = ""

    # 5) Re-force le nombre de lignes (header + n)
    trim_table_to_row_count(table, header_r + 1 + n)





meth_en = get_excel_value(ws, headers, row_idx, "Control Point Control Methodology")
meth_fr = get_excel_value(ws, headers, row_idx, "Control Point Control Methodology Local Language")

fill_verification_table(doc, cp_ref_clean, meth_en, meth_fr)
