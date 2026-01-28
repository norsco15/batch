import pandas as pd
from typing import Union, Optional
from pathlib import Path

EXCLUDED_STATES_OPEN = {"retired", "cancelled", "closed"}

def _read_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
) -> pd.DataFrame:
    return pd.read_excel(risk_cards_path, sheet_name=sheet_name, engine="openpyxl")

def _norm_series(s: pd.Series) -> pd.Series:
    # normalisation robuste (NaN -> "", trim + lowercase)
    return s.fillna("").astype(str).str.strip().str.lower()

def RSK_GAI_002_count_open_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    excluded_states: Optional[set[str]] = None,
) -> int:
    """
    RSK_GAI_002 — Nombre de risk cards OPEN (comptées par 'Local risk reference' unique).
    OPEN = State not in {Retired, Cancelled, Closed}
    """
    excluded = {s.lower() for s in (excluded_states or EXCLUDED_STATES_OPEN)}
    df = _read_risk_cards(risk_cards_path, sheet_name)

    for c in (state_col, local_risk_ref_col):
        if c not in df.columns:
            raise ValueError(f"Colonne '{c}' introuvable. Colonnes dispo: {list(df.columns)}")

    state_norm = _norm_series(df[state_col])
    open_mask = ~state_norm.isin(excluded)

    refs = df.loc[open_mask, local_risk_ref_col].dropna().astype(str).str.strip()
    return int(refs.nunique())

def RSK_GAI_003_count_open_major_extreme_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    residual_risk_level_col: str = "Residual risk level",
    included_levels: Optional[set[str]] = None,
    excluded_states: Optional[set[str]] = None,
) -> int:
    """
    RSK_GAI_003 — Nombre de risk cards OPEN (même périmètre que RSK_GAI_002)
    dont 'Residual risk level' est Major ou Extreme.
    """
    excluded = {s.lower() for s in (excluded_states or EXCLUDED_STATES_OPEN)}
    levels = {str(v).strip().lower() for v in (included_levels or {"3 - Major", "4 - Extreme"})}

    df = _read_risk_cards(risk_cards_path, sheet_name)

    required = [state_col, local_risk_ref_col, residual_risk_level_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}. Colonnes dispo: {list(df.columns)}")

    state_norm = _norm_series(df[state_col])
    open_mask = ~state_norm.isin(excluded)

    rr_norm = _norm_series(df[residual_risk_level_col])
    level_mask = rr_norm.isin(levels)

    refs = df.loc[open_mask & level_mask, local_risk_ref_col].dropna().astype(str).str.strip()
    return int(refs.nunique())

def RSK_GAI_004_count_closed_or_retired_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    state_eval_col: str = "State (Evaluation Status)",
    local_risk_ref_col: str = "Local risk reference",
    included_states: Optional[set[str]] = None,
) -> int:
    """
    RSK_GAI_004 — Nombre de risk cards dont le statut (State (Evaluation Status)) est Closed ou Retired,
    comptées par 'Local risk reference' DISTINCT.
    """
    states = {s.lower() for s in (included_states or {"closed", "retired"})}

    df = _read_risk_cards(risk_cards_path, sheet_name)

    required = [state_eval_col, local_risk_ref_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}. Colonnes dispo: {list(df.columns)}")

    status_norm = _norm_series(df[state_eval_col])
    mask = status_norm.isin(states)

    refs = df.loc[mask, local_risk_ref_col].dropna().astype(str).str.strip()
    return int(refs.nunique())

def write_metrics_to_excel(metrics: list[tuple[str, int]], output_path: Union[str, Path]) -> None:
    df_out = pd.DataFrame(metrics, columns=["Indicator", "Value"])
    df_out.to_excel(output_path, index=False, engine="openpyxl")

def main():
    # ======== À ADAPTER =========
    risk_cards_path = "risk_cards.xlsx"
    risk_cards_sheet = 0  # ou "RiskCards"
    output_path = "resultats_indicateurs.xlsx"
    # ============================

    metrics: list[tuple[str, int]] = []

    metrics.append((
        "RSK_GAI_002",
        RSK_GAI_002_count_open_risk_cards(
            risk_cards_path=risk_cards_path,
            sheet_name=risk_cards_sheet,
            state_col="State",
            local_risk_ref_col="Local risk reference",
        ),
    ))

    metrics.append((
        "RSK_GAI_003",
        RSK_GAI_003_count_open_major_extreme_risk_cards(
            risk_cards_path=risk_cards_path,
            sheet_name=risk_cards_sheet,
            state_col="State",
            local_risk_ref_col="Local risk reference",
            residual_risk_level_col="Residual risk level",
            included_levels={"3 - Major", "4 - Extreme"},
        ),
    ))

    metrics.append((
        "RSK_GAI_004",
        RSK_GAI_004_count_closed_or_retired_risk_cards(
            risk_cards_path=risk_cards_path,
            sheet_name=risk_cards_sheet,
            state_eval_col="State (Evaluation Status)",
            local_risk_ref_col="Local risk reference",
            included_states={"Closed", "Retired"},
        ),
    ))

    write_metrics_to_excel(metrics, output_path)
    print(f"Fichier généré: {output_path}")

if __name__ == "__main__":
    main()
