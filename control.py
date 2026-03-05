from openpyxl import load_workbook
from typing import Dict, List, Tuple
import random

# =========================
# CONFIG
# =========================
FILE_PATH = "control.xlsx"     # <-- ton fichier
OUTPUT_PATH = "control_sampled.xlsx"

SHEET_MAIN = "Sheet1"          # <-- feuille 1 (Number A, Type B, AP C)
SHEET_AP   = "Sheet2"          # <-- feuille 2 (Number A, AP en F ou G)

MAIN_COL_NUMBER = "A"
MAIN_COL_TYPE   = "B"
MAIN_COL_AP     = "C"
MAIN_COL_PICK   = "D"          # on met "YES" si sélectionné

AP_COL_NUMBER = "A"
AP_COL_AP_F   = "F"
AP_COL_AP_G   = "G"

HEADER_ROW = 1
DATA_START_ROW = 2

EXPECTED_DISTINCT_AP = 13
MAX_PER_AP = 6

# Cibles par type (si possible)
TYPE_TARGETS = {
    "standard": 2,
    "emergency": 2,
    "normal": 2,
}

RANDOM_SEED = 42  # fixe pour reproductibilité; mets None si tu veux du vrai aléatoire

# =========================
# Helpers
# =========================
def is_empty(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "")

def norm(s) -> str:
    return "" if is_empty(s) else str(s).strip()

def norm_type(t) -> str:
    return norm(t).lower()

def pick_ap_value(vf, vg):
    """AP = F si rempli sinon G, sinon vide."""
    if not is_empty(vf):
        return norm(vf)
    if not is_empty(vg):
        return norm(vg)
    return ""

def iter_rows_until_blank(ws, col_letter: str, start_row: int, max_empty: int = 30):
    """Iterate rows, stop after max_empty consecutive empty keys in col."""
    empty_streak = 0
    r = start_row
    while True:
        key = ws[f"{col_letter}{r}"].value
        if is_empty(key):
            empty_streak += 1
            if empty_streak >= max_empty:
                break
            r += 1
            continue
        empty_streak = 0
        yield r
        r += 1

def stable_shuffle(lst: List[int], rng: random.Random):
    lst2 = lst[:]
    rng.shuffle(lst2)
    return lst2

# =========================
# Main
# =========================
def run_sampling():
    rng = random.Random(RANDOM_SEED) if RANDOM_SEED is not None else random.Random()

    wb = load_workbook(FILE_PATH)
    ws_main = wb[SHEET_MAIN]
    ws_ap = wb[SHEET_AP]

    # 1) Construire mapping Number -> AP (depuis sheet 2)
    ap_map: Dict[str, str] = {}
    for r in iter_rows_until_blank(ws_ap, AP_COL_NUMBER, DATA_START_ROW):
        number = norm(ws_ap[f"{AP_COL_NUMBER}{r}"].value)
        ap_val = pick_ap_value(ws_ap[f"{AP_COL_AP_F}{r}"].value, ws_ap[f"{AP_COL_AP_G}{r}"].value)
        if number and ap_val:
            ap_map[number] = ap_val

    # 2) Remplir colonne C de sheet 1 + reset sélection
    #    On garde aussi: row_index par AP et par type
    main_rows_by_ap: Dict[str, List[int]] = {}
    main_meta: Dict[int, Tuple[str, str, str]] = {}  # row -> (number, type, ap)

    for r in iter_rows_until_blank(ws_main, MAIN_COL_NUMBER, DATA_START_ROW):
        number = norm(ws_main[f"{MAIN_COL_NUMBER}{r}"].value)
        t = norm_type(ws_main[f"{MAIN_COL_TYPE}{r}"].value)
        ap_val = ap_map.get(number, "")

        ws_main[f"{MAIN_COL_AP}{r}"].value = ap_val
        ws_main[f"{MAIN_COL_PICK}{r}"].value = ""  # reset

        main_meta[r] = (number, t, ap_val)
        if ap_val:
            main_rows_by_ap.setdefault(ap_val, []).append(r)

    distinct_aps = sorted([ap for ap in main_rows_by_ap.keys() if ap.strip() != ""])
    print(f"AP distincts trouvés: {len(distinct_aps)} -> {distinct_aps}")

    if len(distinct_aps) != EXPECTED_DISTINCT_AP:
        print(f"⚠️ Stop: attendu {EXPECTED_DISTINCT_AP} AP distincts, trouvé {len(distinct_aps)}. Aucun échantillonnage effectué.")
        wb.save(OUTPUT_PATH)
        print(f"✅ Fichier sauvegardé (AP remplis quand même): {OUTPUT_PATH}")
        return

    # 3) Echantillonnage par AP (max 6) avec cible de types
    selected_rows: List[int] = []

    for ap in distinct_aps:
        rows = main_rows_by_ap.get(ap, [])
        if not rows:
            continue

        # Partitionner par type
        rows_by_type: Dict[str, List[int]] = {"standard": [], "emergency": [], "normal": [], "other": []}
        for r in rows:
            _, t, _ = main_meta[r]
            if t in rows_by_type:
                rows_by_type[t].append(r)
            else:
                rows_by_type["other"].append(r)

        # Shuffle pour aléatoire stable
        for k in rows_by_type:
            rows_by_type[k] = stable_shuffle(rows_by_type[k], rng)

        picks: List[int] = []

        # 3a) Prendre les quotas 2/2/2 si possible
        for typ, quota in TYPE_TARGETS.items():
            take = min(quota, len(rows_by_type[typ]))
            picks.extend(rows_by_type[typ][:take])
            rows_by_type[typ] = rows_by_type[typ][take:]

        # 3b) Compléter jusqu’à MAX_PER_AP avec ce qui reste (standard/emergency/normal/other)
        remaining_pool = rows_by_type["standard"] + rows_by_type["emergency"] + rows_by_type["normal"] + rows_by_type["other"]
        remaining_pool = stable_shuffle(remaining_pool, rng)

        need = min(MAX_PER_AP, len(rows)) - len(picks)
        if need > 0:
            picks.extend(remaining_pool[:need])

        # Si moins de 6 au total, on prend tout (déjà géré par min)
        selected_rows.extend(picks)

    # 4) Marquer la sélection en colonne D
    for r in selected_rows:
        ws_main[f"{MAIN_COL_PICK}{r}"].value = "YES"

    wb.save(OUTPUT_PATH)
    print(f"✅ Echantillonnage terminé. Sélection totale: {len(selected_rows)} lignes.")
    print(f"✅ Fichier sauvegardé: {OUTPUT_PATH}")

if __name__ == "__main__":
    run_sampling()