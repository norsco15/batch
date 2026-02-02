import pandas as pd
from typing import Union, Optional, Tuple
from pathlib import Path
from datetime import date

EXCLUDED_OPEN_STATES = {"retired", "cancelled", "closed"}

def _read_excel(path: Union[str, Path], sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

def _norm(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip().str.lower()

def _to_dt(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce")

def _first_day(year: int, month: int) -> pd.Timestamp:
    return pd.Timestamp(year=year, month=month, day=1)

def _add_months(ts: pd.Timestamp, months: int) -> pd.Timestamp:
    return ts + pd.DateOffset(months=months)

def _validated_mask(df: pd.DataFrame, status_col: str, sub_state_col: str) -> pd.Series:
    st = _norm(df[status_col])
    sub = _norm(df[sub_state_col])
    return (st == "managed") | ((st == "respond") & (sub == "implementation"))

def _open_mask(df: pd.DataFrame, state_col: str, excluded_open_states: Optional[set[str]] = None) -> pd.Series:
    excluded = {x.lower() for x in (excluded_open_states or EXCLUDED_OPEN_STATES)}
    return ~_norm(df[state_col]).isin(excluded)

def _riskid_to_localrefs(df: pd.DataFrame, risk_id_col: str, local_ref_col: str) -> pd.DataFrame:
    tmp = df[[risk_id_col, local_ref_col]].copy()
    tmp[risk_id_col] = tmp[risk_id_col].astype(str).str.strip()
    tmp[local_ref_col] = tmp[local_ref_col].astype(str).str.strip()

    mp = (
        tmp.dropna(subset=[risk_id_col])
           .groupby(risk_id_col)[local_ref_col]
           .apply(lambda x: "; ".join(sorted({v for v in x if v and v.lower() != "nan"})))
           .reset_index()
           .rename(columns={local_ref_col: "Local risk reference(s)"})
    )
    return mp

def RSK_GPI_006_percent_monthly_validated_with_overdue_and_due_next_2m_over_open_with_details(
    risk_cards_path: Union[str, Path],
    ipt_path: Union[str, Path],
    risk_cards_sheet: Union[str, int] = 0,
    ipt_sheet: Union[str, int] = 0,
    # period = month you report on (e.g. January 2026)
    period_year: Optional[int] = None,
    period_month: Optional[int] = None,
    # risk cards columns
    risk_id_col: str = "Risk ID",
    local_ref_col: str = "Local risk reference",
    state_col: str = "State",
    status_col: str = "Status",
    sub_state_col: str = "Sub-State",
    excluded_open_states: Optional[set[str]] = None,
    # ipt columns
    ipt_risk_id_col: str = "Risk ID",
    planned_end_date_col: str = "Planned end date",
) -> Tuple[float, pd.DataFrame]:
    """
    RSK-GPI-006 (%):
      ( # Risk IDs VALIDATED (scope OPEN) having:
          - >=1 IPT overdue as of end of period month (planned_end < first_day(next_month))
          - AND >=1 IPT finishing in the next 2 months (planned_end in [first_day(next_month), first_day(period_month+3)) )
        ) / (# Risk IDs OPEN) * 100

    Returns:
      percent (0..100) and details DataFrame with:
        Risk ID | Local risk reference(s) | Overdue_IPT_Count | Due_Next2M_IPT_Count
    """
    df_risk = _read_excel(risk_cards_path, risk_cards_sheet)
    df_ipt = _read_excel(ipt_path, ipt_sheet)

    # default period = "previous month" relative to today (useful if you run early next month)
    if period_year is None or period_month is None:
        today = date.today()
        # previous month
        if today.month == 1:
            period_year, period_month = today.year - 1, 12
        else:
            period_year, period_month = today.year, today.month - 1

    required_risk = [risk_id_col, local_ref_col, state_col, status_col, sub_state_col]
    missing = [c for c in required_risk if c not in df_risk.columns]
    if missing:
        raise ValueError(f"RSK-GPI-006 missing risk columns: {missing}. Found: {list(df_risk.columns)}")

    required_ipt = [ipt_risk_id_col, planned_end_date_col]
    missing = [c for c in required_ipt if c not in df_ipt.columns]
    if missing:
        raise ValueError(f"RSK-GPI-006 missing IPT columns: {missing}. Found: {list(df_ipt.columns)}")

    # Time boundaries based on PERIOD month
    period_start = _first_day(period_year, period_month)
    next_month_start = _add_months(period_start, 1)
    month_plus3_start = _add_months(period_start, 3)  # exclusive upper bound (covers next 2 months)

    # Denominator: OPEN (Risk IDs)
    om = _open_mask(df_risk, state_col=state_col, excluded_open_states=excluded_open_states)
    open_ids = set(df_risk.loc[om, risk_id_col].dropna().astype(str).str.strip().tolist())
    denom = len(open_ids)
    if denom == 0:
        empty = pd.DataFrame(columns=[risk_id_col, "Local risk reference(s)", "Overdue_IPT_Count", "Due_Next2M_IPT_Count"])
        return 0.0, empty

    # Validated within OPEN
    df_open = df_risk.loc[om].copy()
    vm = _validated_mask(df_open, status_col=status_col, sub_state_col=sub_state_col)
    validated_open_ids = set(df_open.loc[vm, risk_id_col].dropna().astype(str).str.strip().tolist())

    # IPT windows
    planned_end = _to_dt(df_ipt[planned_end_date_col])
    ipt_risk_ids = df_ipt[ipt_risk_id_col].dropna().astype(str).str.strip()

    overdue_mask = planned_end.notna() & (planned_end < next_month_start)
    due_next2m_mask = planned_end.notna() & (planned_end >= next_month_start) & (planned_end < month_plus3_start)

    # Count IPT per Risk ID for each mask
    overdue_counts = (
        pd.DataFrame({risk_id_col: ipt_risk_ids[overdue_mask].values})
        .groupby(risk_id_col).size().reset_index(name="Overdue_IPT_Count")
    )
    due_counts = (
        pd.DataFrame({risk_id_col: ipt_risk_ids[due_next2m_mask].values})
        .groupby(risk_id_col).size().reset_index(name="Due_Next2M_IPT_Count")
    )

    # Candidate Risk IDs = validated_open_ids that appear in BOTH overdue and due_next2m sets
    overdue_ids = set(overdue_counts[risk_id_col].tolist())
    due_ids = set(due_counts[risk_id_col].tolist())

    numerator_ids = sorted(validated_open_ids.intersection(overdue_ids).intersection(due_ids))
    numerator = len(numerator_ids)

    percent = float((numerator / denom) * 100.0)

    # Details
    df_num_risk = df_risk[df_risk[risk_id_col].astype(str).str.strip().isin(numerator_ids)][[risk_id_col, local_ref_col]].copy()
    mp = _riskid_to_localrefs(df_num_risk, risk_id_col, local_ref_col)

    details = (
        mp.merge(overdue_counts, on=risk_id_col, how="left")
          .merge(due_counts, on=risk_id_col, how="left")
          .fillna({"Overdue_IPT_Count": 0, "Due_Next2M_IPT_Count": 0})
    )
    details["Overdue_IPT_Count"] = details["Overdue_IPT_Count"].astype(int)
    details["Due_Next2M_IPT_Count"] = details["Due_Next2M_IPT_Count"].astype(int)

    # keep only numerator ids (safety)
    details = details[details[risk_id_col].isin(numerator_ids)].copy()

    return percent, details
