import pandas as pd
from typing import Union, Optional
from pathlib import Path

EXCLUDED_STATES_OPEN = {"retired", "cancelled", "closed"}

# --------------------
# Helpers
# --------------------
def _read_excel(path: Union[str, Path], sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

def _norm_series(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip().str.lower()

def _strip_series(s: pd.Series) -> pd.Series:
    return s.dropna().astype(str).str.strip()

def _open_mask(df: pd.DataFrame, state_col: str, excluded_states_open: set[str]) -> pd.Series:
    return ~_norm_series(df[state_col]).isin(excluded_states_open)

# --------------------
# Base indicator: RSK-GAI-002 (Open)
# --------------------
def RSK_GAI_002_count_open_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    excluded_states_open: Optional[set[str]] = None,
) -> int:
    excluded = {s.lower() for s in (excluded_states_open or EXCLUDED_STATES_OPEN)}
    df = _read_excel(risk_cards_path, sheet_name)

    for c in (state_col, local_risk_ref_col):
        if c not in df.columns:
            raise ValueError(f"Colonne '{c}' introuvable (risk cards). Colonnes dispo: {list(df.columns)}")

    om = _open_mask(df, state_col, excluded)
    refs = _strip_series(df.loc[om, local_risk_ref_col])
    return int(refs.nunique())

# --------------------
# Validated OPEN refs
# --------------------
def get_validated_open_risk_card_refs(
    df_risk: pd.DataFrame,
    state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    excluded_states_open: Optional[set[str]] = None,
    status_col: str = "Status",
    sub_state_col: str = "Sub-State",
    managed_value: str = "Managed",
    respond_value: str = "Respond",
    implementation_value: str = "Implementation",
) -> set[str]:
    required = [state_col, local_risk_ref_col, status_col, sub_state_col]
    missing = [c for c in required if c not in df_risk.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes (risk cards): {missing}. Colonnes dispo: {list(df_risk.columns)}")

    excluded = {s.lower() for s in (excluded_states_open or EXCLUDED_STATES_OPEN)}
    df_open = df.loc[_open_mask(df_risk, state_col, excluded)].copy()

    status_norm = _norm_series(df_open[status_col])
    sub_norm = _norm_series(df_open[sub_state_col])

    managed_mask = status_norm == managed_value.strip().lower()
    respond_impl_mask = (status_norm == respond_value.strip().lower()) & (sub_norm == implementation_value.strip().lower())

    validated_mask = managed_mask | respond_impl_mask
    return set(_strip_series(df_open.loc[validated_mask, local_risk_ref_col]).tolist())

# --------------------
# RSK-GPI-007 (ratio)
# --------------------
def RSK_GPI_007_ratio_validated_major_with_postponed_18m_over_open(
    risk_cards_path: Union[str, Path],
    ipt_path: Union[str, Path],
    risk_cards_sheet: Union[str, int] = 0,
    ipt_sheet: Union[str, int] = 0,
    # risk cards columns
    risk_state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    risk_status_col: str = "Status",
    risk_sub_state_col: str = "Sub-State",
    residual_risk_level_col: str = "Residual risk level",
    major_value: str = "3 - Major",
    # ipt columns
    ipt_local_risk_ref_col: str = "Local risk reference",
    initial_due_date_col: str = "Initial due Date",
    planned_end_date_col: str = "Planned end date",
    # config
    excluded_states_open: Optional[set[str]] = None,
) -> float:
    """
    RSK-GPI-007 — Ratio = (# risk cards VALIDATED & MAJOR ayant >=1 IPT postponed >18 mois) / (# risk cards OPEN)

    IPT postponed >18 mois:
      Planned end date > Initial due Date + 18 mois

    Important:
    - Si 'Initial due Date' n'est pas renseignée => IPT ignoré (ne compte pas comme postponed).
    - On compte en DISTINCT 'Local risk reference'.
    """
    excluded = {s.lower() for s in (excluded_states_open or EXCLUDED_STATES_OPEN)}

    df_risk = _read_excel(risk_cards_path, risk_cards_sheet)
    df_ipt = _read_excel(ipt_path, ipt_sheet)

    # Checks risk
    for c in (risk_state_col, local_risk_ref_col, residual_risk_level_col, risk_status_col, risk_sub_state_col):
        if c not in df_risk.columns:
            raise ValueError(f"Colonne '{c}' introuvable (risk cards). Colonnes dispo: {list(df_risk.columns)}")

    # Checks IPT
    for c in (ipt_local_risk_ref_col, initial_due_date_col, planned_end_date_col):
        if c not in df_ipt.columns:
            raise ValueError(f"Colonne '{c}' introuvable (IPT). Colonnes dispo: {list(df_ipt.columns)}")

    # Denominator: OPEN risk cards (distinct local risk reference)
    open_mask = _open_mask(df_risk, risk_state_col, excluded)
    open_refs = set(_strip_series(df_risk.loc[open_mask, local_risk_ref_col]).tolist())
    denom_open = len(open_refs)
    if denom_open == 0:
        return 0.0

    # Numerator scope: VALIDATED & MAJOR (within OPEN)
    validated_refs = get_validated_open_risk_card_refs(
        df_risk=df_risk,
        state_col=risk_state_col,
        local_risk_ref_col=local_risk_ref_col,
        excluded_states_open=excluded_states_open,
        status_col=risk_status_col,
        sub_state_col=risk_sub_state_col,
    )

    rr_norm = _norm_series(df_risk[residual_risk_level_col])
    major_mask = rr_norm == major_value.strip().lower()
    major_refs = set(_strip_series(df_risk.loc[major_mask, local_risk_ref_col]).tolist())

    validated_major_refs = validated_refs.intersection(major_refs).intersection(open_refs)

    if not validated_major_refs:
        return 0.0

    # IPT postponed > 18 months (ignore IPT if initial due date missing)
    init_due = pd.to_datetime(df_ipt[initial_due_date_col], errors="coerce")
    planned_end = pd.to_datetime(df_ipt[planned_end_date_col], errors="coerce")

    # Ignore when Initial due Date missing
    mask_has_init = init_due.notna()
    threshold = init_due + pd.DateOffset(months=18)
    postponed_mask = mask_has_init & planned_end.notna() & (planned_end > threshold)

    postponed_refs = set(_strip_series(df_ipt.loc[postponed_mask, ipt_local_risk_ref_col]).tolist())

    # Numerator: validated_major that have at least one postponed IPT
    num_refs = validated_major_refs.intersection(postponed_refs)
    numerator = len(num_refs)

    return float(numerator / denom_open)

# --------------------
# Output + main
# --------------------
def write_metrics_to_excel(metrics: list[tuple[str, float]], output_path: Union[str, Path]) -> None:
    pd.DataFrame(metrics, columns=["Indicator", "Value"]).to_excel(output_path, index=False, engine="openpyxl")

def main():
    # ======== À ADAPTER =========
    risk_cards_path = "risk_cards.xlsx"
    ipt_path = "ipt.xlsx"
    risk_cards_sheet = 0
    ipt_sheet = 0
    output_path = "resultats_indicateurs.xlsx"
    # ============================

    metrics: list[tuple[str, float]] = []

    # RSK-GAI-002 (count) - utile si tu veux l'écrire aussi dans le fichier
    rsk_gai_002 = RSK_GAI_002_count_open_risk_cards(
        risk_cards_path=risk_cards_path,
        sheet_name=risk_cards_sheet,
        state_col="State",
        local_risk_ref_col="Local risk reference",
    )
    # Exemple: on l'écrit aussi
    metrics.append(("RSK-GAI-002", float(rsk_gai_002)))

    # RSK-GPI-007 (ratio)
    rsk_gpi_007 = RSK_GPI_007_ratio_validated_major_with_postponed_18m_over_open(
        risk_cards_path=risk_cards_path,
        ipt_path=ipt_path,
        risk_cards_sheet=risk_cards_sheet,
        ipt_sheet=ipt_sheet,
        risk_state_col="State",
        local_risk_ref_col="Local risk reference",
        residual_risk_level_col="Residual risk level",
        major_value="3 - Major",
        initial_due_date_col="Initial due Date",
        planned_end_date_col="Planned end date",
    )
    metrics.append(("RSK-GPI-007", rsk_gpi_007))

    write_metrics_to_excel(metrics, output_path)
    print(f"Fichier généré: {output_path}")

if __name__ == "__main__":
    main()
