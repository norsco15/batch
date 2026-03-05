from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string as col_idx
from datetime import datetime, date
from typing import Any, Optional, Set, Dict, Tuple

# =========================
# CONFIG
# =========================
SHEET_DEST_1 = "ITG0080-CHG-RUL002-REQ001-STD1"
SHEET_DEST_2 = "ITG0080-CHGAT-RUL001-REQ001-STD"

SHEET_CHG  = "Sample of changes"
SHEET_TASK = "List of tasks"
SHEET_AFFECTED_CI = "Affected CI on change"

HEADER_ROW = 1
DATA_START_ROW = 2
MAX_ROWS = 40

TEXT_ALL_ELEMENTS = "All elements required are in [CHG][BP2I][Audit][RCG] list of tasks (40 SAMPLES)"
TEXT_M = "Change process declines ITG V6.2 process \n STD is the result of the controls"
TEXT_Q = "Implementation team is responsible of the DE/DI updates."

# =========================
# Helpers
# =========================
def cell(ws, col_letter: str, row: int):
    return ws.cell(row=row, column=col_idx(col_letter))

def getv(ws, col_letter: str, row: int):
    return cell(ws, col_letter, row).value

def setv(ws, col_letter: str, row: int, value):
    cell(ws, col_letter, row).value = value

def is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    return False

def note_0_if_filled_1_if_empty(v: Any) -> int:
    return 0 if not is_empty(v) else 1

def normalize_str(v: Any) -> str:
    return "" if is_empty(v) else str(v).strip()

def normalize_lower(v: Any) -> str:
    return normalize_str(v).lower()

def try_number(v: Any) -> Optional[float]:
    if is_empty(v):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", ".").strip())
    except Exception:
        return None

def build_lookup(ws, key_col: str, value_col: str, start_row=DATA_START_ROW, max_empty=50) -> Dict[str, Any]:
    """
    Build dict key->value by scanning a sheet.
    Stop after max_empty consecutive empty keys.
    """
    d = {}
    empty_streak = 0
    r = start_row
    while True:
        k = getv(ws, key_col, r)
        if is_empty(k):
            empty_streak += 1
            if empty_streak >= max_empty:
                break
            r += 1
            continue
        empty_streak = 0
        d[normalize_str(k)] = getv(ws, value_col, r)
        r += 1
    return d

def sum_notes(ws, row: int, note_cols: list) -> int:
    total = 0
    for c in note_cols:
        v = getv(ws, c, row)
        if isinstance(v, str) and v.strip().upper() == "NA":
            continue
        n = try_number(v)
        if n is not None:
            total += int(n)
    return total

# =========================
# Fill sheet 2
# =========================
def fill_ITG0080_CHGAT_RUL001_REQ001_STD(wb):
    ws_dest = wb[SHEET_DEST_2]
    ws_chg  = wb[SHEET_CHG]
    ws_task = wb[SHEET_TASK]
    ws_aci  = wb[SHEET_AFFECTED_CI]

    # Lookups to emulate RECHERCHEV:
    # A = VLOOKUP(ChangeID, Affected CI on change!A:F, 6) => key A, value F
    aci_lookup = build_lookup(ws_aci, key_col="A", value_col="F")

    # E/G = VLOOKUP(ChangeID, List of tasks!A:K, 11) => key A, value K
    task_k_lookup = build_lookup(ws_task, key_col="A", value_col="K")

    # K = VLOOKUP(ChangeID, List of tasks!A:P, 16) => key A, value P
    task_p_lookup = build_lookup(ws_task, key_col="A", value_col="P")

    NOTE_COLS_FOR_W = ["B", "D", "F", "H", "J", "L", "P", "T", "V"]

    for i in range(MAX_ROWS):
        r = DATA_START_ROW + i
        change_id = getv(ws_chg, "A", r)
        if is_empty(change_id):
            break
        change_id_str = normalize_str(change_id)

        # A = lookup in Affected CI on change
        a_val = aci_lookup.get(change_id_str, None)
        setv(ws_dest, "A", r, a_val)
        setv(ws_dest, "B", r, note_0_if_filled_1_if_empty(a_val))

        # C = Sample V
        c_val = getv(ws_chg, "V", r)
        setv(ws_dest, "C", r, c_val)
        setv(ws_dest, "D", r, note_0_if_filled_1_if_empty(c_val))

        # E rule based on Sample M else lookup tasks K
        m_val = normalize_lower(getv(ws_chg, "M", r))
        if m_val == "emergency":
            e_val = "emergency change"
        elif m_val == "standard":
            e_val = "Standard change"
        else:
            e_val = task_k_lookup.get(change_id_str, None)
        setv(ws_dest, "E", r, e_val)

        # F: NA for Emergency/Standard; else 0 if E filled else 1
        if m_val in ("emergency", "standard"):
            f_val = "NA"
        else:
            f_val = note_0_if_filled_1_if_empty(e_val)
        setv(ws_dest, "F", r, f_val)

        # G = lookup tasks K (same as VLOOKUP A:K col 11)
        g_val = task_k_lookup.get(change_id_str, None)
        setv(ws_dest, "G", r, g_val)
        setv(ws_dest, "H", r, note_0_if_filled_1_if_empty(g_val))

        # I = Sample X
        i_val = getv(ws_chg, "X", r)
        setv(ws_dest, "I", r, i_val)
        setv(ws_dest, "J", r, note_0_if_filled_1_if_empty(i_val))

        # K = lookup tasks P (A:P col 16)
        k_val = task_p_lookup.get(change_id_str, None)
        setv(ws_dest, "K", r, k_val)
        setv(ws_dest, "L", r, note_0_if_filled_1_if_empty(k_val))

        # M constant text, N=0
        setv(ws_dest, "M", r, TEXT_M)
        setv(ws_dest, "N", r, 0)

        # O = Sample Y
        o_val = getv(ws_chg, "Y", r)
        setv(ws_dest, "O", r, o_val)

        # P = NA if no word 'Obsolescence' in O else 0
        o_str = normalize_lower(o_val)
        if "obsolescence" in o_str:
            p_val = 0
        else:
            p_val = "NA"
        setv(ws_dest, "P", r, p_val)

        # Q constant, R=0
        setv(ws_dest, "Q", r, TEXT_Q)
        setv(ws_dest, "R", r, 0)

        # S = Sample U ; T note
        s_val = getv(ws_chg, "U", r)
        setv(ws_dest, "S", r, s_val)
        setv(ws_dest, "T", r, note_0_if_filled_1_if_empty(s_val))

        # U = Sample W ; V note
        u_val = getv(ws_chg, "W", r)
        setv(ws_dest, "U", r, u_val)
        setv(ws_dest, "V", r, note_0_if_filled_1_if_empty(u_val))

        # W = SUM of note columns
        setv(ws_dest, "W", r, sum_notes(ws_dest, r, NOTE_COLS_FOR_W))

# =========================
# Runner
# =========================
def run_fill(control_xlsx_path: str, output_xlsx_path: str):
    wb = load_workbook(control_xlsx_path)

    # Ici tu appelles tes 2 fillers :
    # 1) fill sheet 1 (si tu as déjà le code précédent, tu le laisses)
    # fill_ITG0080_CHG_RUL002_REQ001_STD1(wb)

    # 2) new sheet
    fill_ITG0080_CHGAT_RUL001_REQ001_STD(wb)

    wb.save(output_xlsx_path)
    print(f"✅ Généré : {output_xlsx_path}")

# Exemple:
# run_fill("control.xlsx", "control_filled.xlsx")