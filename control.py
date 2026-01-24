def fill_selective_rule(doc, rule_en: str, rule_fr: str):
    header_text = "Control Point Selective Rule"
    found = find_cell_containing(doc, header_text)
    if not found:
        raise ValueError(f"Header introuvable dans Word: '{header_text}'")

    table, r, c = found
    if r + 1 >= len(table.rows):
        raise IndexError(f"Pas de ligne sous le header '{header_text}'")

    target_cell = table.rows[r + 1].cells[c]
    write_en_fr_in_cell(target_cell, rule_en, rule_fr)




rule_en = get_excel_value(ws, headers, row_idx, "Control Point Selective Rule")
rule_fr = get_excel_value(ws, headers, row_idx, "Control Point Selective Rule Local Language")



fill_selective_rule(doc, rule_en, rule_fr)
