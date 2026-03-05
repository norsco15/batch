from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string as col_idx
from datetime import datetime, date
from typing import Any, Optional, Set

# =========================
# CONFIG
# =========================
SHEET_DEST = "ITG0080-CHG-RUL002-REQ001-STD1"
SHEET_CHG  = "Sample of changes"
SHEET_TASK = "List of tasks"

HEADER_ROW = 1
DATA_START_ROW = 2
MAX_ROWS = 40  # tu peux changer si besoin

TEXT_ALL_ELEMENTS = "All elements required are in [CHG][BP2I][Audit][RCG] list of tasks (40 SAMPLES)"

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
    """Try to convert to float if possible."""
    if is_empty(v):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", ".").strip())
    except Exception:
        return None

def diff_excel(a: Any, b: Any) -> Optional[float]:
    """
    Compute (a - b).
    - If a,b are datetime/date => returns diff in days (float)
    - If numeric => returns numeric difference
    - Else None
    """
    if is_empty(a) or is_empty(b):
        return None

    # dates / datetimes
    if isinstance(a, (datetime, date)) and isinstance(b, (datetime, date)):
        da = a if isinstance(a, datetime) else datetime.combine(a, datetime.min.time())
        db = b if isinstance(b, datetime) else datetime.combine(b, datetime.min.time())
        return (da - db).total_seconds() / 86400.0

    # numbers
    na = try_number(a)
    nb = try_number(b)
    if na is not None and nb is not None:
        return na - nb

    return None

def join_non_empty(values, sep: str) -> str:
    parts = [normalize_str(v) for v in values if not is_empty(v)]
    return sep.join(parts)

def build_bad_changes_from_tasks(ws_tasks) -> Set[str]:
    """
    According to your rule:
    - Look at List of tasks column S
    - If any task has value 'Unsuccessful' (case-insensitive), take its change ID from column A
    """
    bad = set()
    # Iterate rows until a long stretch of empties in column A (simple stop condition)
    empty_streak = 0
    r = DATA_START_ROW
    while True:
        chg_id = getv(ws_tasks, "A", r)
        if is_empty(chg_id):
            empty_streak += 1
            if empty_streak >= 20:
                break
            r += 1
            continue
        empty_streak = 0

        status = getv(ws_tasks, "S", r)
        if normalize_lower(status) == "unsuccessful":
            bad.add(normalize_str(chg_id))
        r += 1
    return bad

# =========================
# Main
# =========================
def run_fill(control_xlsx_path: str, output_xlsx_path: str):
    wb = load_workbook(control_xlsx_path)
    ws_dest = wb[SHEET_DEST]
    ws_chg  = wb[SHEET_CHG]
    ws_task = wb[SHEET_TASK]

    # Precompute: changes that have at least one unsuccessful task
    bad_changes = build_bad_changes_from_tasks(ws_task)

    # Define which DEST columns are "note columns" for BP sum
    # (On prend les paires 0/1 + autres notes jusqu’à BO)
    NOTE_COLS_FOR_BP = [
        "B","D","F","H","J","L","N","P","R","T","V","X","Z","AB","AD","AF","AH",
        "AK","AM","AO","AQ","AS","AU","AW","AY","BA","BC","BE","BG","BI","BK","BO"
    ]

    for i in range(MAX_ROWS):
        r = DATA_START_ROW + i

        # Stop if no change ID in Sample of changes!A
        chg_id = getv(ws_chg, "A", r)
        if is_empty(chg_id):
            break

        chg_id_str = normalize_str(chg_id)

        # -------------------------
        # Simple copies + notes
        # -------------------------
        # A <- chg A
        setv(ws_dest, "A", r, getv(ws_chg, "A", r))
        setv(ws_dest, "B", r, note_0_if_filled_1_if_empty(getv(ws_dest, "A", r)))

        setv(ws_dest, "C", r, getv(ws_chg, "B", r))
        setv(ws_dest, "D", r, note_0_if_filled_1_if_empty(getv(ws_dest, "C", r)))

        setv(ws_dest, "E", r, getv(ws_chg, "AG", r))
        setv(ws_dest, "F", r, note_0_if_filled_1_if_empty(getv(ws_dest, "E", r)))

        setv(ws_dest, "G", r, getv(ws_chg, "L", r))
        setv(ws_dest, "H", r, note_0_if_filled_1_if_empty(getv(ws_dest, "G", r)))

        setv(ws_dest, "I", r, getv(ws_chg, "M", r))
        setv(ws_dest, "J", r, note_0_if_filled_1_if_empty(getv(ws_dest, "I", r)))

        setv(ws_dest, "K", r, getv(ws_chg, "AH", r))
        setv(ws_dest, "L", r, note_0_if_filled_1_if_empty(getv(ws_dest, "K", r)))

        setv(ws_dest, "M", r, getv(ws_chg, "AI", r))
        setv(ws_dest, "N", r, note_0_if_filled_1_if_empty(getv(ws_dest, "M", r)))

        setv(ws_dest, "O", r, getv(ws_chg, "Y", r))
        setv(ws_dest, "P", r, note_0_if_filled_1_if_empty(getv(ws_dest, "O", r)))

        setv(ws_dest, "Q", r, getv(ws_chg, "R", r))
        setv(ws_dest, "R", r, note_0_if_filled_1_if_empty(getv(ws_dest, "Q", r)))

        setv(ws_dest, "S", r, getv(ws_chg, "C", r))
        setv(ws_dest, "T", r, note_0_if_filled_1_if_empty(getv(ws_dest, "S", r)))

        setv(ws_dest, "U", r, getv(ws_chg, "S", r))
        setv(ws_dest, "V", r, note_0_if_filled_1_if_empty(getv(ws_dest, "U", r)))

        setv(ws_dest, "W", r, getv(ws_chg, "T", r))
        setv(ws_dest, "X", r, note_0_if_filled_1_if_empty(getv(ws_dest, "W", r)))

        setv(ws_dest, "Y", r, getv(ws_chg, "U", r))
        setv(ws_dest, "Z", r, note_0_if_filled_1_if_empty(getv(ws_dest, "Y", r)))

        setv(ws_dest, "AA", r, getv(ws_chg, "V", r))
        setv(ws_dest, "AB", r, note_0_if_filled_1_if_empty(getv(ws_dest, "AA", r)))

        setv(ws_dest, "AC", r, getv(ws_chg, "W", r))
        setv(ws_dest, "AD", r, note_0_if_filled_1_if_empty(getv(ws_dest, "AC", r)))

        setv(ws_dest, "AE", r, getv(ws_chg, "X", r))
        setv(ws_dest, "AF", r, note_0_if_filled_1_if_empty(getv(ws_dest, "AE", r)))

        # AG = CONCAT( Sample(O) ; Sample(AJ) )
        ag_val = join_non_empty([getv(ws_chg, "O", r), getv(ws_chg, "AJ", r)], sep=" ")
        setv(ws_dest, "AG", r, ag_val)
        setv(ws_dest, "AH", r, note_0_if_filled_1_if_empty(getv(ws_dest, "AG", r)))

        # AI <- E ; AJ <- F ; AK note pair (both filled => 0 else 1)
        setv(ws_dest, "AI", r, getv(ws_chg, "E", r))
        setv(ws_dest, "AJ", r, getv(ws_chg, "F", r))
        ai_val = getv(ws_dest, "AI", r)
        aj_val = getv(ws_dest, "AJ", r)
        setv(ws_dest, "AK", r, 0 if (not is_empty(ai_val) and not is_empty(aj_val)) else 1)

        # AL constant ; AM = 0
        setv(ws_dest, "AL", r, TEXT_ALL_ELEMENTS)
        setv(ws_dest, "AM", r, 0)

        # AN rule: if Sample(M) == 'Standard' => 'Standard change' else Sample(AK)
        if normalize_lower(getv(ws_chg, "M", r)) == "standard":
            an_val = "Standard change"
        else:
            an_val = getv(ws_chg, "AK", r)
        setv(ws_dest, "AN", r, an_val)

        # AO rule:
        # - if standard change => NA
        # - else => 0 if filled, 1 if empty (on AN)
        if normalize_lower(getv(ws_chg, "M", r)) == "standard":
            setv(ws_dest, "AO", r, "NA")
        else:
            setv(ws_dest, "AO", r, note_0_if_filled_1_if_empty(getv(ws_dest, "AN", r)))

        # AP = join Sample(AC,AD,AE) with ", "
        ap_val = join_non_empty([getv(ws_chg, "AC", r), getv(ws_chg, "AD", r), getv(ws_chg, "AE", r)], sep=", ")
        setv(ws_dest, "AP", r, ap_val)

        # AQ: 0 if ALL three filled, else 1
        acv, adv, aev = getv(ws_chg, "AC", r), getv(ws_chg, "AD", r), getv(ws_chg, "AE", r)
        setv(ws_dest, "AQ", r, 0 if (not is_empty(acv) and not is_empty(adv) and not is_empty(aev)) else 1)

        # AR = join Sample(G,H) with "| "
        ar_val = join_non_empty([getv(ws_chg, "G", r), getv(ws_chg, "H", r)], sep="| ")
        setv(ws_dest, "AR", r, ar_val)
        # AS: 0 if BOTH filled, else 1
        gsv, hsv = getv(ws_chg, "G", r), getv(ws_chg, "H", r)
        setv(ws_dest, "AS", r, 0 if (not is_empty(gsv) and not is_empty(hsv)) else 1)

        # AT constant ; AU = 0
        setv(ws_dest, "AT", r, TEXT_ALL_ELEMENTS)
        setv(ws_dest, "AU", r, 0)

        # AV = Sample(J) ; AW note
        setv(ws_dest, "AV", r, getv(ws_chg, "J", r))
        setv(ws_dest, "AW", r, note_0_if_filled_1_if_empty(getv(ws_dest, "AV", r)))

        # AX = Sample(AA) ; AY note
        setv(ws_dest, "AX", r, getv(ws_chg, "AA", r))
        setv(ws_dest, "AY", r, note_0_if_filled_1_if_empty(getv(ws_dest, "AX", r)))

        # AZ = Sample(I) ; BA note
        setv(ws_dest, "AZ", r, getv(ws_chg, "I", r))
        setv(ws_dest, "BA", r, note_0_if_filled_1_if_empty(getv(ws_dest, "AZ", r)))

        # -------------------------
        # Tasks logic: BB/BC and BJ/BK
        # -------------------------
        close_code_change = normalize_lower(getv(ws_chg, "J", r))  # you said "colonne J sample of changes"
        is_unsuccessful_change = close_code_change == "unsuccessful"

        if is_unsuccessful_change:
            bb_text = "Unsucessful"  # keep your spelling
            bb_note = "NA"
        else:
            # Check if THIS change id has any unsuccessful task (based on tasks sheet scan)
            if chg_id_str in bad_changes:
                bb_text = "Closed code d'une ou plusieurs tâches : unsuccessful [CHG][BP2I][Audit][RCG] list of tasks (40 SAMPLES)"
            else:
                bb_text = "Closed code des tâches : successful [CHG][BP2I][Audit][RCG] list of tasks (40 SAMPLES)"
            bb_note = 0  # as you requested for the rest

        setv(ws_dest, "BB", r, bb_text)
        setv(ws_dest, "BC", r, bb_note)

        # BJ/BK same logic as BB/BC
        setv(ws_dest, "BJ", r, bb_text)
        setv(ws_dest, "BK", r, bb_note)

        # -------------------------
        # Date diffs: BD/BE and BF/BG
        # BD = Sample(G) - Sample(E)
        bd_val = diff_excel(getv(ws_chg, "G", r), getv(ws_chg, "E", r))
        setv(ws_dest, "BD", r, bd_val)

        # BE: if BD positive => 0 else:
        #      if AV (close code) unsuccessful => 0 else if successful => 1
        if bd_val is not None and bd_val > 0:
            be_val = 0
        else:
            be_val = 0 if is_unsuccessful_change else 1
        setv(ws_dest, "BE", r, be_val)

        # BF = Sample(H) - Sample(F)
        bf_val = diff_excel(getv(ws_chg, "H", r), getv(ws_chg, "F", r))
        setv(ws_dest, "BF", r, bf_val)

        # BG: if BF negative => 0 else:
        #      if AV unsuccessful => 0 else successful => 1
        if bf_val is not None and bf_val < 0:
            bg_val = 0
        else:
            bg_val = 0 if is_unsuccessful_change else 1
        setv(ws_dest, "BG", r, bg_val)

        # -------------------------
        # BH/BI
        # -------------------------
        setv(ws_dest, "BH", r, getv(ws_chg, "AF", r))
        setv(ws_dest, "BI", r, note_0_if_filled_1_if_empty(getv(ws_dest, "BH", r)))

        # -------------------------
        # BL/BM
        # BL = Concat(BE,BG) ; BM = sum(BE+BG)
        # (Concat => "BE BG" pour être lisible)
        setv(ws_dest, "BL", r, f"{getv(ws_dest, 'BE', r)} {getv(ws_dest, 'BG', r)}")
        # sum: ignore non-numeric (ex: 'NA')
        be_num = try_number(getv(ws_dest, "BE", r)) or 0
        bg_num = try_number(getv(ws_dest, "BG", r)) or 0
        setv(ws_dest, "BM", r, be_num + bg_num)

        # -------------------------
        # BN/BO
        # BN = BH ; BO note on BN
        setv(ws_dest, "BN", r, getv(ws_dest, "BH", r))
        setv(ws_dest, "BO", r, note_0_if_filled_1_if_empty(getv(ws_dest, "BN", r)))

        # -------------------------
        # BP = SUM of note columns (B, D, F, ... up to BO)
        # Treat "NA" as 0
        total = 0
        for c in NOTE_COLS_FOR_BP:
            v = getv(ws_dest, c, r)
            if isinstance(v, str) and v.strip().upper() == "NA":
                continue
            n = try_number(v)
            if n is not None:
                total += n
        setv(ws_dest, "BP", r, total)

    wb.save(output_xlsx_path)
    print(f"✅ Généré : {output_xlsx_path}")


# Exemple d’exécution:
# run_fill("control.xlsx", "control_filled.xlsx")