from datetime import datetime
from pathlib import Path
from copy import copy

import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter


# ============================================================
# CONFIG
# ============================================================

EXTRACT_FILE = r"extract_ipt.xlsx"            # à modifier
TRACKING_FILE = r"suivi.xlsx"                 # à modifier
OUTPUT_FILE = r"suivi_updated.xlsx"           # suivi mis à jour
SUMMARY_FILE = r"ipt_summary.xlsx"            # nouveau fichier de synthèse

EXTRACT_SHEET_NAME = "Extract IPT"
NUMBER_COL = "Number"
PLANNED_END_DATE_COL = "Planned end date"
RISK_ID_COL = "Risk ID"
PERCENT_COMPLETE_COL = "Percent Complete"

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
    12: "novembre",
    12: "décembre",
}

ENGLISH_MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


# ============================================================
# HELPERS GENERAUX
# ============================================================

def normalize_col_name(name):
    if name is None:
        return None
    return str(name).strip()


def normalize_sheet_name(name):
    if name is None:
        return None
    return str(name).strip().lower()


def clean_percent_value(value):
    """
    Transforme Percent Complete en nombre si possible.
    Gère les cas :
    - 0
    - 15
    - 15%
    - '15 %'
    - 0.15 (si jamais)
    """
    if pd.isna(value):
        return None

    if isinstance(value, str):
        v = value.strip().replace("%", "").replace(",", ".")
        if v == "":
            return None
        try:
            num = float(v)
        except ValueError:
            return None
    else:
        try:
            num = float(value)
        except Exception:
            return None

    # Si la valeur ressemble à une fraction Excel (0.15 = 15%)
    if 0 <= num <= 1:
        return num * 100

    return num


def load_extract_dataframe(extract_file):
    df = pd.read_excel(extract_file, dtype=object)
    df.columns = [normalize_col_name(c) for c in df.columns]

    mandatory_cols = [NUMBER_COL, PLANNED_END_DATE_COL, RISK_ID_COL, PERCENT_COMPLETE_COL]
    for col in mandatory_cols:
        if col not in df.columns:
            raise ValueError(f"Colonne obligatoire absente dans l'extract : '{col}'")

    df[NUMBER_COL] = df[NUMBER_COL].astype(str).str.strip()
    df[PLANNED_END_DATE_COL] = pd.to_datetime(df[PLANNED_END_DATE_COL], errors="coerce")
    df[RISK_ID_COL] = df[RISK_ID_COL].astype(str).str.strip()
    df["_PercentCompleteNumeric"] = df[PERCENT_COMPLETE_COL].apply(clean_percent_value)

    return df


def get_month_targets(base_date=None, nb_months=3):
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

        targets.append(
            (
                target_year,
                target_month,
                FRENCH_MONTHS[target_month],
                ENGLISH_MONTHS[target_month],
            )
        )

    return targets


def find_sheet_case_insensitive(wb, target_name):
    target_norm = normalize_sheet_name(target_name)
    for sheet_name in wb.sheetnames:
        if normalize_sheet_name(sheet_name) == target_norm:
            return wb[sheet_name]
    return None


def get_header_map(ws):
    header_map = {}
    for col_idx in range(1, ws.max_column + 1):
        value = ws.cell(row=1, column=col_idx).value
        if value is not None:
            header_map[normalize_col_name(value)] = col_idx
    return header_map


def ws_headers(ws):
    headers = []
    for col_idx in range(1, ws.max_column + 1):
        headers.append(normalize_col_name(ws.cell(row=1, column=col_idx).value))
    return headers


def read_sheet_as_dataframe(ws):
    data = list(ws.values)
    if not data:
        return pd.DataFrame()

    headers = [normalize_col_name(c) for c in data[0]]
    rows = data[1:]
    return pd.DataFrame(rows, columns=headers)


def month_filter(df, year, month):
    return df[
        (df[PLANNED_END_DATE_COL].dt.year == year) &
        (df[PLANNED_END_DATE_COL].dt.month == month)
    ].copy()


# ============================================================
# HELPERS STYLES / FORMAT EXCEL
# ============================================================

def copy_cell_style(source_cell, target_cell):
    if source_cell.has_style:
        target_cell._style = copy(source_cell._style)
        target_cell.font = copy(source_cell.font)
        target_cell.fill = copy(source_cell.fill)
        target_cell.border = copy(source_cell.border)
        target_cell.alignment = copy(source_cell.alignment)
        target_cell.number_format = copy(source_cell.number_format)
        target_cell.protection = copy(source_cell.protection)


def copy_column_style(ws, source_col_idx, target_col_idx):
    for row_idx in range(1, ws.max_row + 1):
        source_cell = ws.cell(row=row_idx, column=source_col_idx)
        target_cell = ws.cell(row=row_idx, column=target_col_idx)
        copy_cell_style(source_cell, target_cell)

    source_letter = get_column_letter(source_col_idx)
    target_letter = get_column_letter(target_col_idx)

    if source_letter in ws.column_dimensions:
        ws.column_dimensions[target_letter].width = ws.column_dimensions[source_letter].width


def copy_row_style(ws, source_row_idx, target_row_idx):
    for col_idx in range(1, ws.max_column + 1):
        source_cell = ws.cell(row=source_row_idx, column=col_idx)
        target_cell = ws.cell(row=target_row_idx, column=col_idx)
        copy_cell_style(source_cell, target_cell)

    if source_row_idx in ws.row_dimensions:
        ws.row_dimensions[target_row_idx].height = ws.row_dimensions[source_row_idx].height


def autosize_columns(ws):
    for col_idx in range(1, ws.max_column + 1):
        max_length = 0
        col_letter = get_column_letter(col_idx)
        for row_idx in range(1, ws.max_row + 1):
            value = ws.cell(row=row_idx, column=col_idx).value
            if value is not None:
                max_length = max(max_length, len(str(value)))
        current_width = ws.column_dimensions[col_letter].width
        target_width = min(max_length + 2, 60)
        if current_width is None or current_width < target_width:
            ws.column_dimensions[col_letter].width = target_width


# ============================================================
# FEUILLE EXTRACT IPT
# ============================================================

def clear_worksheet_content(ws):
    for row in ws.iter_rows():
        for cell in row:
            cell.value = None


def ensure_extract_sheet(wb, extract_df):
    if EXTRACT_SHEET_NAME in wb.sheetnames:
        ws = wb[EXTRACT_SHEET_NAME]
        clear_worksheet_content(ws)
    else:
        ws = wb.create_sheet(EXTRACT_SHEET_NAME)

    export_df = extract_df.drop(columns=["_PercentCompleteNumeric"], errors="ignore")

    for col_idx, col_name in enumerate(export_df.columns, start=1):
        ws.cell(row=1, column=col_idx, value=col_name)

    for row_idx, row in enumerate(export_df.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    return ws


# ============================================================
# COMMENTAIRES / AJOUTS / FERMETURES
# ============================================================

def get_or_create_comment_column(ws, comment_header, planned_end_date_col_name):
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
    copy_column_style(ws, planned_col_idx, insert_at)
    ws.cell(row=1, column=insert_at, value=comment_header)

    return insert_at


def append_new_ipts(ws, extract_subset, comment_col_idx, month_name_fr):
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

    common_cols = [col for col in ws_headers(ws) if col in to_add.columns]

    added_count = 0
    style_template_row = ws.max_row if ws.max_row >= 2 else None

    for _, row in to_add.iterrows():
        new_row_idx = ws.max_row + 1

        if style_template_row is not None and style_template_row >= 2:
            copy_row_style(ws, style_template_row, new_row_idx)

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


def mark_closed_ipts(ws, extract_subset, comment_col_idx):
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


# ============================================================
# SYNTHÈSE MENSUELLE
# ============================================================

def build_month_summary_row(extract_subset, month_name_en, status_label):
    total_ipts = len(extract_subset)

    risk_ids = (
        extract_subset[RISK_ID_COL]
        .dropna()
        .astype(str)
        .str.strip()
    )
    risk_ids = risk_ids[risk_ids != ""]
    distinct_risk_ids = risk_ids.nunique()

    pct = extract_subset["_PercentCompleteNumeric"]

    lt_50 = pct.apply(lambda x: x is not None and pd.notna(x) and x < 50).sum()
    eq_0 = pct.apply(lambda x: x is not None and pd.notna(x) and x == 0).sum()

    return {
        "Status": status_label,
        "Month": month_name_en,
        "IPTs on RLs": f"{total_ipts} IPTs on {distinct_risk_ids} RLs",
        "IPTs <50%": f"{lt_50} IPTs <50%",
        "IPTs = 0%": f"Dont {eq_0} IPTs = 0%",
        "Total IPTs": total_ipts,
        "Distinct Risk IDs": distinct_risk_ids,
        "IPTs Percent < 50": int(lt_50),
        "IPTs Percent = 0": int(eq_0),
    }


def write_summary_excel(summary_rows, output_file):
    df = pd.DataFrame(summary_rows)

    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"

    headers = list(df.columns)
    for col_idx, header in enumerate(headers, start=1):
        ws.cell(row=1, column=col_idx, value=header)

    for row_idx, row in enumerate(df.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    autosize_columns(ws)
    wb.save(output_file)


# ============================================================
# MAIN
# ============================================================

def main():
    today = datetime.today()
    day_str = str(today.day)
    month_name_today_fr = FRENCH_MONTHS[today.month]
    comment_header = f"Comments {day_str} {month_name_today_fr}"
    status_label = f"Status {today.year} {ENGLISH_MONTHS[today.month]} {today.day:02d}"

    extract_path = Path(EXTRACT_FILE)
    tracking_path = Path(TRACKING_FILE)

    if not extract_path.exists():
        raise FileNotFoundError(f"Fichier extract introuvable : {EXTRACT_FILE}")
    if not tracking_path.exists():
        raise FileNotFoundError(f"Fichier de suivi introuvable : {TRACKING_FILE}")

    extract_df = load_extract_dataframe(EXTRACT_FILE)
    wb = load_workbook(TRACKING_FILE)

    # 1) Mise à jour du fichier de suivi
    ensure_extract_sheet(wb, extract_df)
    autosize_columns(wb[EXTRACT_SHEET_NAME])

    # 2) Traitement mois courant + 2 mois suivants
    targets = get_month_targets(today, nb_months=3)
    summary = []
    summary_rows = []

    for year, month_num, month_name_fr, month_name_en in targets:
        ws = find_sheet_case_insensitive(wb, month_name_fr)

        extract_subset = month_filter(extract_df, year, month_num)

        # construire la synthèse même si la feuille mensuelle n'existe pas
        summary_rows.append(
            build_month_summary_row(
                extract_subset=extract_subset,
                month_name_en=month_name_en,
                status_label=status_label,
            )
        )

        if ws is None:
            summary.append(f"[WARNING] Feuille '{month_name_fr}' absente, mois ignoré pour le suivi.")
            continue

        comment_col_idx = get_or_create_comment_column(
            ws,
            comment_header=comment_header,
            planned_end_date_col_name=PLANNED_END_DATE_COL,
        )

        added = append_new_ipts(ws, extract_subset, comment_col_idx, month_name_fr)
        closed = mark_closed_ipts(ws, extract_subset, comment_col_idx)

        autosize_columns(ws)

        summary.append(
            f"[OK] Feuille '{ws.title}' : {len(extract_subset)} IPT dans l'extract, "
            f"{added} ajoutée(s), {closed} marquée(s) Closed."
        )

    wb.save(OUTPUT_FILE)

    # 3) Export fichier de synthèse
    write_summary_excel(summary_rows, SUMMARY_FILE)

    print("Traitement terminé.")
    print(f"Fichier de suivi généré : {OUTPUT_FILE}")
    print(f"Fichier de synthèse généré : {SUMMARY_FILE}")
    print("\nRésumé :")
    for line in summary:
        print(line)


if __name__ == "__main__":
    main()