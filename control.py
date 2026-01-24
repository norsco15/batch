def trim_table_to_row_count(table, target_rows: int):
    while len(table.rows) > target_rows:
        remove_row(table, len(table.rows) - 1)



def fill_selective_rule(doc, rule_en: str, rule_fr: str):
    header_text = "Control Point Selective Rule"
    found = find_cell_containing(doc, header_text)
    if not found:
        raise ValueError(f"Header introuvable dans Word: '{header_text}'")

    table, r, c = found

    # ✅ Force le tableau à n’avoir que le header + 1 ligne de contenu
    # (on garde toutes les lignes jusqu'à r+1 inclus)
    trim_table_to_row_count(table, r + 2)

    # Écrit dans la cellule en dessous
    target_cell = table.rows[r + 1].cells[c]
    write_en_fr_in_cell(target_cell, rule_en, rule_fr)

    # ✅ Re-force après écriture (par sécurité)
    trim_table_to_row_count(table, r + 2)
