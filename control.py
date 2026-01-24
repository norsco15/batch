import re

def extract_intro_and_bullets(text: str):
    """
    Retourne (intro, bullets)
    - intro = texte avant la 1ère bulle
    - bullets = liste des sous-points (sans le 'o')
    Détecte les bulles de type: 'o xxx' (o en tant que token)
    """
    if not text:
        return "", []

    s = str(text).replace("\r", "\n")
    s = re.sub(r"\s+", " ", s).strip()  # normalisation légère (comme dans Excel)

    # Split sur le token bullet "o " quand il est séparé (début ou après espace/ : ; )
    # Ex: "describe: o item1 o item2"
    parts = re.split(r'(?:(?<=^)|(?<=[\s:;]))o\s+', s)

    intro = parts[0].strip()
    bullets = [p.strip() for p in parts[1:] if p.strip()]
    return intro, bullets




def fill_verification_table(doc, cp_ref_clean: str, meth_en: str, meth_fr: str):
    # Split par interpoint '·' -> V1, V2, V3, ...
    en_points = split_by_interpoint(meth_en)
    fr_points = split_by_interpoint(meth_fr)

    n_main = max(len(en_points), len(fr_points))
    if n_main == 0:
        return

    # Trouver le tableau "Verification ID"
    res = find_table_and_header_row(doc, "Verification ID")
    if not res:
        raise ValueError("Table 'Verification ID' introuvable dans le Word.")
    table, header_r, _ = res

    # Nettoyer : garder jusqu'au header inclus (supprime lignes fantômes)
    trim_table_to_row_count(table, header_r + 1)

    # Construire toutes les lignes à écrire (liste de tuples: (id, en_text, fr_text))
    rows_to_write = []

    for i in range(n_main):
        v_num = i + 1
        en_text = en_points[i] if i < len(en_points) else ""
        fr_text = fr_points[i] if i < len(fr_points) else ""

        en_intro, en_bullets = extract_intro_and_bullets(en_text)
        fr_intro, fr_bullets = extract_intro_and_bullets(fr_text)

        # S'il y a des bulles (EN ou FR), on génère Vx-01, Vx-02, ...
        if en_bullets or fr_bullets:
            nb = max(len(en_bullets), len(fr_bullets))
            for j in range(nb):
                sub = j + 1
                verif_id = f"{cp_ref_clean}-V{v_num}-{sub:02d}"

                en_b = en_bullets[j] if j < len(en_bullets) else ""
                fr_b = fr_bullets[j] if j < len(fr_bullets) else ""

                # Texte final : intro + retour ligne + "o ..." (si la bulle existe)
                en_final = (en_intro + (" o " + en_b if en_b else "")).strip()
                fr_final = (fr_intro + (" o " + fr_b if fr_b else "")).strip()

                rows_to_write.append((verif_id, en_final, fr_final))
        else:
            # Pas de bulles -> on garde Vx
            verif_id = f"{cp_ref_clean}-V{v_num}"
            rows_to_write.append((verif_id, en_text.strip(), fr_text.strip()))

    # Ajouter exactement le bon nombre de lignes
    for _ in range(len(rows_to_write)):
        table.add_row()

    # Remplir les lignes
    for idx, (verif_id, en_val, fr_val) in enumerate(rows_to_write):
        row = table.rows[header_r + 1 + idx]
        row.cells[0].text = verif_id
        write_en_fr_in_cell(row.cells[1], en_val, fr_val)
        row.cells[2].text = ""  # Result
        row.cells[3].text = ""  # Evidence

    # Re-force : header + N lignes (supprime fantômes éventuels)
    trim_table_to_row_count(table, header_r + 1 + len(rows_to_write))
