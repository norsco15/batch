import pandas as pd
from pathlib import Path
from typing import Union, Optional, Tuple, Dict
from datetime import date

EXCLUDED_OPEN_STATES = {"retired", "cancelled", "closed"}

# -------------------------
# Helpers
# -------------------------
def _read_excel(path: Union[str, Path], sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

def _norm(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip().str.lower()

def _to_dt(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce")

def _yyyymm(dt: pd.Series) -> pd.Series:
    return dt.dt.year * 100 + dt.dt.month

def _riskid_to_localrefs(df: pd.DataFrame, risk_id_col: str, local_ref_col: str) -> pd.DataFrame:
    """
    Retourne un DataFrame mapping unique:
      Risk ID | Local risk reference (concaténée si plusieurs)
    """
    if risk_id_col not in df.columns or local_ref_col not in df.columns:
        raise ValueError(f"Mapping requires '{risk_id_col}' and '{local_ref_col}'. Found: {list(df.columns)}")

    tmp = df[[risk_id_col, local_ref_col]].copy()
    tmp[risk_id_col] = tmp[risk_id_col].astype(str).str.strip()
    tmp[local_ref_col] = tmp[local_ref_col].astype(str).str.strip()

    # groupby Risk ID -> concat unique local refs
    mp = (
        tmp.dropna(subset=[risk_id_col])
           .groupby(risk_id_col)[local_ref_col]
           .apply(lambda x: "; ".join(sorted({v for v in x if v and v.lower() != "nan"})))
           .reset_index()
           .rename(columns={local_ref_col: "Local risk reference(s)"})
    )
    return mp

def _validated_mask(
    df: pd.DataFrame,
    status_col: str = "Status",
    sub_state_col: str = "Sub-State",
    managed_value: str = "Managed",
    respond_value: str = "Respond",
    implementation_value: str = "Implementation",
) -> pd.Series:
    st = _norm(df[status_col])
    sub = _norm(df[sub_state_col])
    return (st == managed_value.lower()) | ((st == respond_value.lower()) & (sub == implementation_value.lower()))

def _open_mask(
    df: pd.DataFrame,
    state_col: str = "State",
    excluded_open_states: Optional[set[str]] = None,
) -> pd.Series:
    excluded = {x.lower() for x in (excluded_open_states or EXCLUDED_OPEN_STATES)}
    return ~_norm(df[state_col]).isin(excluded)

# -------------------------
# Base: OPEN count (Risk ID)
# -------------------------
def RSK_GAI_002_open_count_by_risk_id(
    df_risk: pd.DataFrame,
    risk_id_col: str = "Risk ID",
    state_col: str = "State",
    excluded_open_states: Optional[set[str]] = None,
) -> int:
    om = _open_mask(df_risk, state_col=state_col, excluded_open_states=excluded_open_states)
    risk_ids = df_risk.loc[om, risk_id_col].dropna().astype(str).str.strip()
    return int(risk_ids.nunique())

def get_open_risk_ids(
    df_risk: pd.DataFrame,
    risk_id_col: str = "Risk ID",
    state_col: str = "State",
    excluded_open_states: Optional[set[str]] = None,
) -> set[str]:
    om = _open_mask(df_risk, state_col=state_col, excluded_open_states=excluded_open_states)
    return set(df_risk.loc[om, risk_id_col].dropna().astype(str).str.strip().tolist())

def get_validated_open_risk_ids(
    df_risk: pd.DataFrame,
    risk_id_col: str = "Risk ID",
    state_col: str = "State",
    excluded_open_states: Optional[set[str]] = None,
    status_col: str = "Status",
    sub_state_col: str = "Sub-State",
) -> set[str]:
    om = _open_mask(df_risk, state_col=state_col, excluded_open_states=excluded_open_states)
    df_open = df_risk.loc[om].copy()
    vm = _validated_mask(df_open, status_col=status_col, sub_state_col=sub_state_col)
    return set(df_open.loc[vm, risk_id_col].dropna().astype(str).str.strip().tolist())

def _major_extreme_risk_ids(
    df_risk: pd.DataFrame,
    risk_id_col: str,
    residual_risk_level_col: str = "Residual risk level",
    major_extreme_values: Optional[set[str]] = None,
) -> set[str]:
    levels = {v.strip().lower() for v in (major_extreme_values or {"3 - Major", "4 - Extreme"})}
    mask = _norm(df_risk[residual_risk_level_col]).isin(levels)
    return set(df_risk.loc[mask, risk_id_col].dropna().astype(str).str.strip().tolist())

# -------------------------
# RSK-GAI-006 (monthly closed/retired) + details
# -------------------------
def RSK_GAI_006_monthly_closed_retired_with_details(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    # columns
    risk_id_col: str = "Risk ID",
    local_ref_col: str = "Local risk reference",
    state_eval_col: str = "State (Evaluation Status)",
    retired_date_col: str = "Risk retirement date",
    closed_date_col: str = "Risk closure date",
    # asof month
    asof_year: Optional[int] = None,
    asof_month: Optional[int] = None,
) -> Tuple[int, pd.DataFrame]:
    df = _read_excel(risk_cards_path, sheet_name)

    required = [risk_id_col, local_ref_col, state_eval_col, retired_date_col, closed_date_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"RSK-GAI-006 missing columns: {missing}. Found: {list(df.columns)}")

    if asof_year is None or asof_month is None:
        today = date.today()
        asof_year, asof_month = today.year, today.month
    asof_key = asof_year * 100 + asof_month

    st = _norm(df[state_eval_col])

    retired_dt = _to_dt(df[retired_date_col])
    closed_dt = _to_dt(df[closed_date_col])

    retired_mask = (st == "retired") & retired_dt.notna() & (_yyyymm(retired_dt) == asof_key)
    closed_mask = (st == "closed") & closed_dt.notna() & (_yyyymm(closed_dt) == asof_key)

    df_ret = df.loc[retired_mask, [risk_id_col, local_ref_col]].copy()
    df_ret["State"] = "Retired"
    df_ret["Event date"] = retired_dt.loc[retired_mask].dt.date.astype(str)

    df_clo = df.loc[closed_mask, [risk_id_col, local_ref_col]].copy()
    df_clo["State"] = "Closed"
    df_clo["Event date"] = closed_dt.loc[closed_mask].dt.date.astype(str)

    df_out = pd.concat([df_ret, df_clo], ignore_index=True)

    # unique by Risk ID (Risk ID is unique, but safe)
    df_out[risk_id_col] = df_out[risk_id_col].astype(str).str.strip()
    df_out[local_ref_col] = df_out[local_ref_col].astype(str).str.strip()
    df_out = df_out.dropna(subset=[risk_id_col]).drop_duplicates(subset=[risk_id_col, "State"])

    # Build mapping (Risk ID -> Local refs concat)
    mp = _riskid_to_localrefs(df_out, risk_id_col, local_ref_col)
    df_details = df_out[[risk_id_col, "State", "Event date"]].merge(mp, on=risk_id_col, how="left")

    count = int(df_details[risk_id_col].nunique())
    return count, df_details

# -------------------------
# RSK-GAI-007 (monthly non validated = open - validated) + details
# -------------------------
def RSK_GAI_007_non_validated_open_with_details(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    # columns
    risk_id_col: str = "Risk ID",
    local_ref_col: str = "Local risk reference",
    state_col: str = "State",
    status_col: str = "Status",
    sub_state_col: str = "Sub-State",
    excluded_open_states: Optional[set[str]] = None,
) -> Tuple[int, pd.DataFrame]:
    df = _read_excel(risk_cards_path, sheet_name)

    required = [risk_id_col, local_ref_col, state_col, status_col, sub_state_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"RSK-GAI-007 missing columns: {missing}. Found: {list(df.columns)}")

    open_ids = get_open_risk_ids(df, risk_id_col=risk_id_col, state_col=state_col, excluded_open_states=excluded_open_states)
    validated_open_ids = get_validated_open_risk_ids(
        df,
        risk_id_col=risk_id_col,
        state_col=state_col,
        excluded_open_states=excluded_open_states,
        status_col=status_col,
        sub_state_col=sub_state_col,
    )
    non_validated_ids = sorted(open_ids - validated_open_ids)

    df_scope = df[df[risk_id_col].astype(str).str.strip().isin(non_validated_ids)].copy()
    mp = _riskid_to_localrefs(df_scope, risk_id_col, local_ref_col)

    # details
    df_details = mp.copy()  # Risk ID + Local risk reference(s)
    count = int(df_details[risk_id_col].nunique())
    return count, df_details

# -------------------------
# RSK-GAI-009 / RSK-GAI-0010 (validated + major/extreme + response + recorded>24m) + details
# -------------------------
def _RSK_GAI_009_0010_core(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int],
    response_value: str,  # "Accept" or "Mitigate"
    # columns
    risk_id_col: str = "Risk ID",
    local_ref_col: str = "Local risk reference",
    state_col: str = "State",
    status_col: str = "Status",
    sub_state_col: str = "Sub-State",
    residual_risk_level_col: str = "Residual risk level",
    response_col: str = "Reponse",
    recorded_date_col: str = "Recorded date",
    # config
    months: int = 24,
    major_extreme_values: Optional[set[str]] = None,
    excluded_open_states: Optional[set[str]] = None,
    asof: Optional[date] = None,
) -> Tuple[int, pd.DataFrame]:
    df = _read_excel(risk_cards_path, sheet_name)

    required = [
        risk_id_col, local_ref_col, state_col, status_col, sub_state_col,
        residual_risk_level_col, response_col, recorded_date_col
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"RSK-GAI-009/0010 missing columns: {missing}. Found: {list(df.columns)}")

    if asof is None:
        asof = date.today()
    threshold = pd.Timestamp(asof) - pd.DateOffset(months=months)

    # Scope: OPEN
    om = _open_mask(df, state_col=state_col, excluded_open_states=excluded_open_states)
    df_open = df.loc[om].copy()

    # Validated
    vm = _validated_mask(df_open, status_col=status_col, sub_state_col=sub_state_col)

    # Major/Extreme
    levels = {v.strip().lower() for v in (major_extreme_values or {"3 - Major", "4 - Extreme"})}
    lm = _norm(df_open[residual_risk_level_col]).isin(levels)

    # Response
    rm = _norm(df_open[response_col]) == response_value.strip().lower()

    # Recorded > 24 months (recorded since more than 24 months)
    rec = _to_dt(df_open[recorded_date_col])
    dm = rec.notna() & (rec <= threshold)

    df_hit = df_open.loc[vm & lm & rm & dm, [risk_id_col, local_ref_col]].copy()
    df_hit[risk_id_col] = df_hit[risk_id_col].astype(str).str.strip()

    mp = _riskid_to_localrefs(df_hit, risk_id_col, local_ref_col)
    count = int(mp[risk_id_col].nunique())
    return count, mp

def RSK_GAI_009_accept_recorded_gt_24m_with_details(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    **kwargs
) -> Tuple[int, pd.DataFrame]:
    return _RSK_GAI_009_0010_core(risk_cards_path, sheet_name, response_value="Accept", **kwargs)

def RSK_GAI_0010_mitigate_recorded_gt_24m_with_details(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    **kwargs
) -> Tuple[int, pd.DataFrame]:
    return _RSK_GAI_009_0010_core(risk_cards_path, sheet_name, response_value="Mitigate", **kwargs)

# -------------------------
# RSK-GPI-007 (percent ratio) + details (nb IPT postponed>18m by Risk ID)
# -------------------------
def RSK_GPI_007_percent_validated_major_extreme_with_ipt_postponed_18m_over_open_with_details(
    risk_cards_path: Union[str, Path],
    ipt_path: Union[str, Path],
    risk_cards_sheet: Union[str, int] = 0,
    ipt_sheet: Union[str, int] = 0,
    # risk columns
    risk_id_col: str = "Risk ID",
    local_ref_col: str = "Local risk reference",
    state_col: str = "State",
    status_col: str = "Status",
    sub_state_col: str = "Sub-State",
    residual_risk_level_col: str = "Residual risk level",
    major_extreme_values: Optional[set[str]] = None,  # {"3 - Major", "4 - Extreme"}
    excluded_open_states: Optional[set[str]] = None,
    # ipt columns
    ipt_risk_id_col: str = "Risk ID",
    initial_due_date_col: str = "Initial due Date",
    planned_end_date_col: str = "Planned end date",
    months_postpone: int = 18,
) -> Tuple[float, pd.DataFrame]:
    """
    - Numerator: Risk IDs that are (OPEN & VALIDATED & Major/Extreme) and have >=1 IPT with:
        Planned end date > Initial due date + 18 months
      and Initial due date must be present (otherwise ignore IPT)
    - Denominator: number of OPEN risk cards (Risk ID unique)
    - Output: percent (0-100) + details:
        Risk ID | Local risk reference(s) | Overdue_IPT_Count
    """
    df_risk = _read_excel(risk_cards_path, risk_cards_sheet)
    df_ipt = _read_excel(ipt_path, ipt_sheet)

    # checks risk
    needed_risk = [risk_id_col, local_ref_col, state_col, status_col, sub_state_col, residual_risk_level_col]
    missing = [c for c in needed_risk if c not in df_risk.columns]
    if missing:
        raise ValueError(f"RSK-GPI-007 missing risk columns: {missing}. Found: {list(df_risk.columns)}")

    # checks ipt
    needed_ipt = [ipt_risk_id_col, initial_due_date_col, planned_end_date_col]
    missing = [c for c in needed_ipt if c not in df_ipt.columns]
    if missing:
        raise ValueError(f"RSK-GPI-007 missing IPT columns: {missing}. Found: {list(df_ipt.columns)}")

    # Denominator: OPEN
    open_ids = get_open_risk_ids(df_risk, risk_id_col=risk_id_col, state_col=state_col, excluded_open_states=excluded_open_states)
    denom = len(open_ids)
    if denom == 0:
        return 0.0, pd.DataFrame(columns=[risk_id_col, "Local risk reference(s)", "Overdue_IPT_Count"])

    # Validated (within open)
    validated_open_ids = get_validated_open_risk_ids(
        df_risk,
        risk_id_col=risk_id_col,
        state_col=state_col,
        excluded_open_states=excluded_open_states,
        status_col=status_col,
        sub_state_col=sub_state_col,
    )

    # Major/Extreme
    major_extreme_ids = _major_extreme_risk_ids(
        df_risk,
        risk_id_col=risk_id_col,
        residual_risk_level_col=residual_risk_level_col,
        major_extreme_values=major_extreme_values or {"3 - Major", "4 - Extreme"},
    )

    target_ids = open_ids.intersection(validated_open_ids).intersection(major_extreme_ids)

    # IPT postponed >18 months (ignore if initial due date missing)
    init_due = _to_dt(df_ipt[initial_due_date_col])
    planned_end = _to_dt(df_ipt[planned_end_date_col])
    has_init = init_due.notna()

    threshold = init_due + pd.DateOffset(months=months_postpone)
    postponed_mask = has_init & planned_end.notna() & (planned_end > threshold)

    # Count postponed IPT per Risk ID
    tmp = df_ipt.loc[postponed_mask, [ipt_risk_id_col]].copy()
    tmp[ipt_risk_id_col] = tmp[ipt_risk_id_col].astype(str).str.strip()
    ipt_counts = (
        tmp.dropna(subset=[ipt_risk_id_col])
           .groupby(ipt_risk_id_col)
           .size()
           .reset_index(name="Overdue_IPT_Count")
           .rename(columns={ipt_risk_id_col: risk_id_col})
    )

    postponed_ids = set(ipt_counts[risk_id_col].tolist())

    numerator_ids = sorted(target_ids.intersection(postponed_ids))
    numerator = len(numerator_ids)

    percent = float((numerator / denom) * 100.0)

    # Details: Risk ID -> Local refs + IPT overdue count
    df_num = df_risk[df_risk[risk_id_col].astype(str).str.strip().isin(numerator_ids)][[risk_id_col, local_ref_col]].copy()
    mp = _riskid_to_localrefs(df_num, risk_id_col, local_ref_col)

    details = mp.merge(ipt_counts, on=risk_id_col, how="left").fillna({"Overdue_IPT_Count": 0})
    details["Overdue_IPT_Count"] = details["Overdue_IPT_Count"].astype(int)

    # Keep only numerator ids (just in case)
    details = details[details[risk_id_col].isin(numerator_ids)].copy()

    return percent, details

# -------------------------
# Excel writer: Summary + Details sheets
# -------------------------
def write_results_to_excel(
    output_path: Union[str, Path],
    summary_rows: list[tuple[str, float]],
    details_sheets: Dict[str, pd.DataFrame],
) -> None:
    summary_df = pd.DataFrame(summary_rows, columns=["Indicator", "Value"])
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        for sheet, df in details_sheets.items():
            safe_name = sheet[:31]  # Excel constraint
            df.to_excel(writer, sheet_name=safe_name, index=False)

# -------------------------
# Example main
# -------------------------
def main():
    risk_cards_path = "risk_cards.xlsx"
    ipt_path = "ipt.xlsx"
    output_path = "resultats_indicateurs.xlsx"

    risk_sheet = 0
    ipt_sheet = 0

    # si tu veux figer un mois (ex Janvier 2026) pour RSK-GAI-006:
    asof_year, asof_month = 2026, 1

    summary: list[tuple[str, float]] = []
    details: Dict[str, pd.DataFrame] = {}

    # --- RSK-GAI-006 ---
    val_006, det_006 = RSK_GAI_006_monthly_closed_retired_with_details(
        risk_cards_path=risk_cards_path,
        sheet_name=risk_sheet,
        risk_id_col="Risk ID",
        local_ref_col="Local risk reference",
        state_eval_col="State (Evaluation Status)",
        retired_date_col="Risk retirement date",
        closed_date_col="Risk closure date",
        asof_year=asof_year,
        asof_month=asof_month,
    )
    summary.append(("RSK-GAI-006", float(val_006)))
    details["RSK-GAI-006_details"] = det_006

    # --- RSK-GAI-007 ---
    val_007, det_007 = RSK_GAI_007_non_validated_open_with_details(
        risk_cards_path=risk_cards_path,
        sheet_name=risk_sheet,
        risk_id_col="Risk ID",
        local_ref_col="Local risk reference",
        state_col="State",
        status_col="Status",
        sub_state_col="Sub-State",
    )
    summary.append(("RSK-GAI-007", float(val_007)))
    details["RSK-GAI-007_details"] = det_007

    # --- RSK-GAI-009 ---
    val_009, det_009 = RSK_GAI_009_accept_recorded_gt_24m_with_details(
        risk_cards_path=risk_cards_path,
        sheet_name=risk_sheet,
        risk_id_col="Risk ID",
        local_ref_col="Local risk reference",
        state_col="State",
        status_col="Status",
        sub_state_col="Sub-State",
        residual_risk_level_col="Residual risk level",
        response_col="Reponse",
        recorded_date_col="Recorded date",
        months=24,
        major_extreme_values={"3 - Major", "4 - Extreme"},
        # asof=date(2026, 1, 31)  # optionnel si tu veux figer T
    )
    summary.append(("RSK-GAI-009", float(val_009)))
    details["RSK-GAI-009_details"] = det_009

    # --- RSK-GAI-0010 ---
    val_0010, det_0010 = RSK_GAI_0010_mitigate_recorded_gt_24m_with_details(
        risk_cards_path=risk_cards_path,
        sheet_name=risk_sheet,
        risk_id_col="Risk ID",
        local_ref_col="Local risk reference",
        state_col="State",
        status_col="Status",
        sub_state_col="Sub-State",
        residual_risk_level_col="Residual risk level",
        response_col="Reponse",
        recorded_date_col="Recorded date",
        months=24,
        major_extreme_values={"3 - Major", "4 - Extreme"},
    )
    summary.append(("RSK-GAI-0010", float(val_0010)))
    details["RSK-GAI-0010_details"] = det_0010

    # --- RSK-GPI-007 (percent + IPT counts) ---
    pct_gpi_007, det_gpi_007 = RSK_GPI_007_percent_validated_major_extreme_with_ipt_postponed_18m_over_open_with_details(
        risk_cards_path=risk_cards_path,
        ipt_path=ipt_path,
        risk_cards_sheet=risk_sheet,
        ipt_sheet=ipt_sheet,
        risk_id_col="Risk ID",
        local_ref_col="Local risk reference",
        state_col="State",
        status_col="Status",
        sub_state_col="Sub-State",
        residual_risk_level_col="Residual risk level",
        major_extreme_values={"3 - Major", "4 - Extreme"},
        ipt_risk_id_col="Risk ID",                # adapte si différent
        initial_due_date_col="Initial due Date",
        planned_end_date_col="Planned end date",
        months_postpone=18,
    )
    summary.append(("RSK-GPI-007", pct_gpi_007))  # déjà en %
    details["RSK-GPI-007_details"] = det_gpi_007

    # Write excel
    write_results_to_excel(output_path, summary, details)
    print(f"OK -> {output_path}")

if __name__ == "__main__":
    main()
