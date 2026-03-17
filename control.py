from datetime import datetime
from pathlib import Path
import calendar

import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


# ============================================================
# CONFIG
# ============================================================

EXTRACT_FILE = r"extract_ipt.xlsx"   # à modifier
TRACKING_FILE = r"suivi.xlsx"        # à modifier
OUTPUT_FILE = r"suivi_updated.xlsx"  # fichier de sortie

EXTRACT_SHEET_NAME = "Extract IPT"
NUMBER_COL = "Number"
PLANNED_END_DATE_COL = "Planned end date"

# Noms des mois en français pour les feuilles
FRENCH_MONTHS = {
    1: "janvier",
    2: "février",
    3: "mars",
    4: "avril",
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre",
    10: "octobre",
    11: "novembre",
    12: "décembre",
}


# ============================================================
# HELPERS
# ============================================================

def normalize_col_name(name):
    if name is None:
        return None
    return str(name).strip()


def load_extract_dataframe(extract_file):
    """
    Lit l'extract IPT.
    """
    df = pd.read_excel(extract_file, dtype=object)
    df.columns = [normalize_col_name(c) for c in df.columns]

    if NUMBER_COL not in df.columns:
        raise ValueError(f"Colonne obligatoire absente dans l'extract : '{NUMBER_COL}'")
    if PLANNED_END_DATE_COL not in df.columns:
        raise ValueError(f"Colonne obligatoire absente dans l'extract : '{PLANNED_END_DATE_COL}'")

    df[PLANNED_END_DATE_COL] = pd.to_datetime(df[PLANNED_END_DATE_COL], errors="coerce")
    df[NUMBER_COL] = df[NUMBER_COL].astype(str).str.strip()

    return df


def get_month_targets(base_date=None, nb_months=3):
    """
    Retourne [(year, month_num, month_name_fr), ...]
    pour le mois courant + nb_months-1 suivants.
    """
    if base_date is None:
        base_date = datetime.today()

    targets = []
    year = base_date.year
    month = base_date.month

    for i in range(nb_months):
        target_month = month + i
        target_year = year

        while target_month > 12:
            target_month -= 12
            target_year += 1

        targets.append((target_year, target_month, FRENCH_MONTHS[target_month]))

    return targets


def get_header_map(ws):
    """
    Retourne un dict {nom_colonne: index_colonne_excel}
    basé sur la première ligne de la feuille.
    """
    header_map = {}
    for col_idx in range(1, ws.max_column + 1):
        value = ws.cell(row=1, column=col_idx).value
        if value is not None:
            header_map[normalize_col_name(value)] = col_idx
    return header_map


def ensure_extract_sheet(wb, extract_df):
    """
    Remplace/crée la feuille Extract IPT avec le contenu brut de l'extract.
    """
    if EXTRACT_SHEET_NAME in wb.sheetnames:
        ws = wb[EXTRACT_SHEET_NAME]
        wb.remove(ws)

    ws = wb.create_sheet(EXTRACT_SHEET_NAME)

    # écrire les headers
    for col_idx, col_name in enumerate(extract_df.columns, start=1):
        ws.cell(row=1, column=col_idx, value=col_name)

    # écrire les données
    for row_idx, row in enumerate(extract_df.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    return ws


def get_or_create_comment_column(ws, comment_header, planned_end_date_col_name):
    """
    Trouve ou crée la colonne commentaire juste à droite de Planned end date.
    Si la colonne existe déjà, la réutilise.
    """
    header_map = get_header_map(ws)

    if comment_header in header_map:
        return header_map[comment_header]

    if planned_end_date_col_name not in header_map:
        raise ValueError(
            f"La feuille '{ws.title}' ne contient pas la colonne '{planned_end_date_col_name}'"
        )

    planned_col_idx = header_map[planned_end_date_col_name]
    insert_at = planned_col_idx + 1

    ws.insert_cols(insert_at)
    ws.cell(row=1, column=insert_at, value=comment_header)

    return insert_at


def read_sheet_as_dataframe(ws):
    """
    Lit la feuille openpyxl en DataFrame pandas.
    """
    data = list(ws.values)
    if not data:
        return pd.DataFrame()

    headers = [normalize_col_name(c) for c in data[0]]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=headers)
    return df


def month_filter(df, year, month):
    """
    Filtre l'extract sur Planned end date = année/mois cible.
    """
    return df[
        (df[PLANNED_END_DATE_COL].dt.year == year) &
        (df[PLANNED_END_DATE_COL].dt.month == month)
    ].copy()


def append_new_ipts(ws, extract_subset, comment_col_idx, month_name_fr):
    """
    Ajoute dans la feuille les IPT présentes dans l'extract
    mais absentes de la feuille destination.
    Ne copie que les colonnes déjà existantes dans la feuille.
    """
    header_map = get_header_map(ws)

    if NUMBER_COL not in header_map:
        raise ValueError(f"La feuille '{ws.title}' ne contient pas la colonne '{NUMBER_COL}'")

    sheet_df = read_sheet_as_dataframe(ws)
    if NUMBER_COL in sheet_df.columns:
        existing_numbers = set(
            sheet_df[NUMBER_COL].dropna().astype(str).str.strip().tolist()
        )
    else:
        existing_numbers = set()

    extract_subset = extract_subset.copy()
    extract_subset[NUMBER_COL] = extract_subset[NUMBER_COL].astype(str).str.strip()

    to_add = extract_subset[~extract_subset[NUMBER_COL].isin(existing_numbers)].copy()

    if to_add.empty:
        return 0

    # colonnes communes entre extract et feuille destination
    common_cols = [col for col in ws_headers(ws) if col in to_add.columns]

    added_count = 0
    for _, row in to_add.iterrows():
        new_row_idx = ws.max_row + 1

        for col_name in common_cols:
            if col_name in header_map:
                ws.cell(row=new_row_idx, column=header_map[col_name], value=row[col_name])

        ws.cell(
            row=new_row_idx,
            column=comment_col_idx,
            value=f"Postponed to {month_name_fr}"
        )
        added_count += 1

    return added_count


def ws_headers(ws):
    headers = []
    for col_idx in range(1, ws.max_column + 1):
        headers.append(normalize_col_name(ws.cell(row=1, column=col_idx).value))
    return headers


def mark_closed_ipts(ws, extract_subset, comment_col_idx):
    """
    Pour les IPT présentes dans la feuille mensuelle
    mais absentes de l'extract du mois correspondant :
    mettre 'Closed' dans la colonne commentaire.
    """
    header_map = get_header_map(ws)

    if NUMBER_COL not in header_map:
        raise ValueError(f"La feuille '{ws.title}' ne contient pas la colonne '{NUMBER_COL}'")

    sheet_number_col = header_map[NUMBER_COL]

    extract_numbers = set(
        extract_subset[NUMBER_COL].dropna().astype(str).str.strip().tolist()
    )

    closed_count = 0
    for row_idx in range(2, ws.max_row + 1):
        sheet_number = ws.cell(row=row_idx, column=sheet_number_col).value
        if sheet_number is None:
            continue

        sheet_number = str(sheet_number).strip()
        if sheet_number not in extract_numbers:
            ws.cell(row=row_idx, column=comment_col_idx, value="Closed")
            closed_count += 1

    return closed_count


def autosize_columns(ws):
    for col_idx in range(1, ws.max_column + 1):
        max_length = 0
        col_letter = get_column_letter(col_idx)
        for row_idx in range(1, ws.max_row + 1):
            value = ws.cell(row=row_idx, column=col_idx).value
            if value is not None:
                max_length = max(max_length, len(str(value)))
        ws.column_dimensions[col_letter].width = min(max_length + 2, 60)


# ============================================================
# MAIN
# ============================================================

def main():
    today = datetime.today()
    day_str = str(today.day)
    month_name_today = FRENCH_MONTHS[today.month]
    comment_header = f"Comments {day_str} {month_name_today}"

    extract_df = load_extract_dataframe(EXTRACT_FILE)

    tracking_path = Path(TRACKING_FILE)
    if not tracking_path.exists():
        raise FileNotFoundError(f"Fichier de suivi introuvable : {TRACKING_FILE}")

    wb = load_workbook(TRACKING_FILE)

    # 1) Charger/remplacer la feuille Extract IPT
    ensure_extract_sheet(wb, extract_df)

    # 2) Traiter mois courant + 2 mois suivants
    targets = get_month_targets(today, nb_months=3)

    summary = []

    for year, month_num, month_sheet_name in targets:
        if month_sheet_name not in wb.sheetnames:
            summary.append(
                f"[WARNING] Feuille '{month_sheet_name}' absente, mois ignoré."
            )
            continue

        ws = wb[month_sheet_name]

        # Filtre extract pour le mois cible
        extract_subset = month_filter(extract_df, year, month_num)

        # créer / récupérer colonne commentaire
        comment_col_idx = get_or_create_comment_column(
            ws,
            comment_header=comment_header,
            planned_end_date_col_name=PLANNED_END_DATE_COL,
        )

        added = append_new_ipts(ws, extract_subset, comment_col_idx, month_sheet_name)
        closed = mark_closed_ipts(ws, extract_subset, comment_col_idx)

        autosize_columns(ws)

        summary.append(
            f"[OK] Feuille '{month_sheet_name}' : {len(extract_subset)} IPT dans l'extract, "
            f"{added} ajoutée(s), {closed} marquée(s) Closed."
        )

    # autosize aussi sur Extract IPT
    autosize_columns(wb[EXTRACT_SHEET_NAME])

    wb.save(OUTPUT_FILE)

    print("Traitement terminé.")
    print(f"Fichier généré : {OUTPUT_FILE}")
    print("\nRésumé :")
    for line in summary:
        print(line)


if __name__ == "__main__":
    main()