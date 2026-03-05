from openpyxl.utils import column_index_from_string as col_idx

# (On réutilise tes helpers existants : getv/setv/is_empty/normalize_lower/note_0_if_filled_1_if_empty/try_number)

SHEET_RCG_DEV23 = "RCG-DEV2,3"

def fill_RCG_DEV23(wb):
    ws_dest = wb[SHEET_RCG_DEV23]
    ws_chg  = wb[SHEET_CHG]  # "Sample of changes"

    NOTE_COLS_FOR_M = ["B", "D", "F", "H", "J", "L"]

    for i in range(MAX_ROWS):
        r = DATA_START_ROW + i

        change_id = getv(ws_chg, "A", r)
        if is_empty(change_id):
            break

        m_type = normalize_lower(getv(ws_chg, "M", r))  # emergency/standard/normal...
        # -------------------
        # A
        # -------------------
        if m_type == "emergency":
            a_val = "emergency change"
        elif m_type == "standard":
            a_val = "standard change"
        else:
            a_val = "BNPP_BP2I_CHG_CAB"
        setv(ws_dest, "A", r, a_val)

        # B : NA for Emergency/Standard; else 0 if not empty
        if a_val in ("emergency change", "standard change"):
            b_val = "NA"
        else:
            b_val = 0 if not is_empty(a_val) else 1  # “0 pour le reste si c pas vide”
        setv(ws_dest, "B", r, b_val)

        # -------------------
        # C
        # -------------------
        if m_type == "emergency":
            c_val = "emergency change"
        elif m_type == "normal":
            c_val = "normal change"
        elif m_type == "standard":
            c_val = "Once a change in a STD no CAB"
        else:
            c_val = "NA"
        setv(ws_dest, "C", r, c_val)

        # D : emergency -> NA, normal -> NA, else 0
        if c_val in ("emergency change", "normal change"):
            d_val = "NA"
        else:
            d_val = 0
        setv(ws_dest, "D", r, d_val)

        # -------------------
        # E (même règle que C)
        # -------------------
        e_val = c_val
        setv(ws_dest, "E", r, e_val)

        # F :
        # 0 si E contient emergency change OU 'Once a change in a STD no CAB'
        # si Normal change => NA
        if e_val in ("emergency change", "Once a change in a STD no CAB"):
            f_val = 0
        elif e_val == "normal change":
            f_val = "NA"
        else:
            # cas “autre/NA” : je mets NA par défaut (on peut ajuster)
            f_val = "NA"
        setv(ws_dest, "F", r, f_val)

        # -------------------
        # G : check column K contains 'SEC'
        # (column K of WHAT? -> j'interprète: colonne K de Sample of changes)
        # -------------------
        k_src = normalize_str(getv(ws_chg, "K", r))
        if "SEC" in k_src.upper():
            g_val = "Change involving IT security controls"
        else:
            g_val = "Change not involving IT security controls"
        setv(ws_dest, "G", r, g_val)

        # H = 0
        setv(ws_dest, "H", r, 0)

        # -------------------
        # I / J
        # I depends on Sample N (TRUE) + Sample O (High)
        # -------------------
        n_val = getv(ws_chg, "N", r)
        o_val = normalize_lower(getv(ws_chg, "O", r))

        is_true = False
        # Excel VRAI peut être bool True, "VRAI", "TRUE", 1...
        if isinstance(n_val, bool):
            is_true = n_val
        else:
            is_true = normalize_lower(n_val) in ("vrai", "true", "1", "yes")

        if is_true and o_val == "high":
            i_val = "Major Change"
        elif is_true:
            i_val = "Cross change"
        else:
            i_val = "NA"
        setv(ws_dest, "I", r, i_val)

        if i_val in ("Cross change", "Major Change"):
            j_val = 0
        else:
            j_val = "NA"
        setv(ws_dest, "J", r, j_val)

        # -------------------
        # K / L (même logique que I/J)
        # -------------------
        k_val = i_val
        setv(ws_dest, "K", r, k_val)

        if k_val in ("Cross change", "Major Change"):
            l_val = 0
        else:
            l_val = "NA"
        setv(ws_dest, "L", r, l_val)

        # -------------------
        # M = sum(B,D,F,H,J,L) en ignorant NA
        # -------------------
        total = 0
        for col in NOTE_COLS_FOR_M:
            v = getv(ws_dest, col, r)
            if isinstance(v, str) and v.strip().upper() == "NA":
                continue
            n = try_number(v)
            if n is not None:
                total += int(n)
        setv(ws_dest, "M", r, total)




SHEET_RCG_DEV24 = "RCG-DEV2,4"

TEXT_A_DEV24 = (
    "An automatic closure in setup in Service Now. Tickets are closed 7 days after implementation task closure "
    "according to information collected into ticket (See change fields in service now for date and hour)"
)
TEXT_C_DEV24 = "All stakeholders can access the information about change results via Service Now"

def fill_RCG_DEV24(wb):
    ws_dest = wb[SHEET_RCG_DEV24]
    ws_chg  = wb[SHEET_CHG]  # Sample of changes

    for i in range(MAX_ROWS):
        r = DATA_START_ROW + i

        # stop condition: same as others
        if is_empty(getv(ws_chg, "A", r)):
            break

        setv(ws_dest, "A", r, TEXT_A_DEV24)
        setv(ws_dest, "B", r, 0)

        setv(ws_dest, "C", r, TEXT_C_DEV24)
        setv(ws_dest, "D", r, 0)

        # E = B + D
        b = try_number(getv(ws_dest, "B", r)) or 0
        d = try_number(getv(ws_dest, "D", r)) or 0
        setv(ws_dest, "E", r, b + d)


SHEET_RCG_DEV25 = "RCG-DEV2,5"

TEXT_A_DEV25 = (
    "The teams in assignement group have the necessary authorization to deploy the changes. "
    "See column Assignement group of Tasks in [CHG][BP2I][Audit][RCG] list of tasks (40 Samples)"
)

def fill_RCG_DEV25(wb):
    ws_dest = wb[SHEET_RCG_DEV25]
    ws_chg  = wb[SHEET_CHG]  # Sample of changes

    for i in range(MAX_ROWS):
        r = DATA_START_ROW + i
        if is_empty(getv(ws_chg, "A", r)):
            break

        setv(ws_dest, "A", r, TEXT_A_DEV25)
        setv(ws_dest, "B", r, 0)



from datetime import datetime, date, timedelta

SHEET_RCG_DEV22 = "RCG-DEV2,2"
SHEET_STD1 = "ITG0080-CHG-RUL002-REQ001-STD1"
SHEET_CHG_RUL001 = "ITG0080-CHG-RUL001-REQ001-STD"     # au cas où elle existe
SHEET_CHGAT_RUL001 = "ITG0080-CHGAT-RUL001-REQ001-STD" # celle qu’on a remplie

TEXT_A_DEV22 = "See sheet ITG0080-CHG-RUL002-REQ001-STD1"
TEXT_C_DEV22 = "See sheets ITG0080-CHG-RUL002-REQ001-STD1 & ITG0080-CHG-RUL001-REQ001-STD"

def to_dt(v):
    if is_empty(v):
        return None
    if isinstance(v, datetime):
        return v
    if isinstance(v, date):
        return datetime.combine(v, datetime.min.time())
    # parfois Excel renvoie string
    try:
        # accepte "YYYY-mm-dd ..." etc.
        return datetime.fromisoformat(str(v).replace("Z", "").strip())
    except Exception:
        return None

def is_weekend(d: datetime) -> bool:
    return d.weekday() >= 5  # 5=Samedi, 6=Dimanche

def business_hours_diff_excl_weekends(start: datetime, end: datetime) -> float:
    """
    Hours between start and end excluding weekends.
    Counts 24h for weekdays (pas de plage 9-18).
    """
    if start is None or end is None:
        return float("inf")
    if end < start:
        start, end = end, start

    cur = start
    total_seconds = 0.0

    while cur.date() <= end.date():
        day_start = cur
        day_end = min(datetime.combine(cur.date(), datetime.max.time()), end)

        if not is_weekend(cur):
            total_seconds += max(0.0, (day_end - day_start).total_seconds())

        # next day at 00:00
        next_day = datetime.combine(cur.date() + timedelta(days=1), datetime.min.time())
        cur = next_day

    return total_seconds / 3600.0

def fill_RCG_DEV22(wb):
    ws_dest = wb[SHEET_RCG_DEV22]
    ws_chg  = wb[SHEET_CHG]        # Sample of changes
    ws_std1 = wb[SHEET_STD1]

    ws_rul001 = wb[SHEET_CHGAT_RUL001]  # ITG0080-CHGAT-RUL001-REQ001-STD
    
    for i in range(MAX_ROWS):
        r = DATA_START_ROW + i

        # stop condition
        if is_empty(getv(ws_chg, "A", r)):
            break

        # A texte
        setv(ws_dest, "A", r, TEXT_A_DEV22)

        # B = BP de STD1
        bp_val = getv(ws_std1, "BP", r)
        setv(ws_dest, "B", r, bp_val)

        # C texte
        setv(ws_dest, "C", r, TEXT_C_DEV22)

        # D = BP(STD1) + W(RUL001)
        w_val = getv(ws_rul001, "W", r)
        bp_num = try_number(bp_val) or 0
        w_num  = try_number(w_val) or 0
        setv(ws_dest, "D", r, bp_num + w_num)

        # --- G/H : contrôle Emergency (72h ouvrées) Created(B) vs Actual start(G) de Sample of changes
        m_type = normalize_lower(getv(ws_chg, "M", r))
        created = to_dt(getv(ws_chg, "B", r))     # Created = colonne B
        actual_start = to_dt(getv(ws_chg, "G", r))# Actual start date = colonne G

        if m_type == "emergency":
            hours = business_hours_diff_excl_weekends(created, actual_start)
            if hours <= 72:
                g_text = "Time frame respected"
                h_val = 0
            else:
                g_text = "Time frame not respected"
                h_val = 1
        else:
            g_text = "Change is not emergency"
            h_val = "NA"

        setv(ws_dest, "G", r, g_text)
        setv(ws_dest, "H", r, h_val)

        # --- I/J : Emergency -> prendre AF, sinon "Change is not emergency"
        if m_type != "emergency":
            i_val = "Change is not emergency"
            j_val = "NA"
        else:
            i_val = getv(ws_chg, "AF", r)  # bool attendu (VRAI/FAUX)
            # J : si I == FAUX -> 0, si VRAI -> 1
            if isinstance(i_val, bool):
                j_val = 1 if i_val else 0
            else:
                i_low = normalize_lower(i_val)
                if i_low in ("vrai", "true", "1", "yes"):
                    j_val = 1
                elif i_low in ("faux", "false", "0", "no"):
                    j_val = 0
                else:
                    # si valeur bizarre/absente => on met 1 (conservateur) ou NA ; ici je mets 1
                    j_val = 1

        setv(ws_dest, "I", r, i_val)
        setv(ws_dest, "J", r, j_val)

        # --- K = somme des colonnes B, D, F, H, J
        # (F n’a pas été défini dans ta spec => on le lit tel quel dans la sheet, sinon 0)
        b = getv(ws_dest, "B", r)
        d = getv(ws_dest, "D", r)
        f = getv(ws_dest, "F", r)  # si vide -> 0
        h = getv(ws_dest, "H", r)
        j = getv(ws_dest, "J", r)

        total = 0
        for v in (b, d, f, h, j):
            if isinstance(v, str) and v.strip().upper() == "NA":
                continue
            n = try_number(v)
            if n is not None:
                total += n

        setv(ws_dest, "K", r, total)