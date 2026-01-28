import pandas as pd
from typing import Union, Optional
from pathlib import Path
from datetime import date

EXCLUDED_STATES_OPEN = {"retired", "cancelled", "closed"}

def _read_risk_cards(path: Union[str, Path], sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

def _norm_series(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip().str.lower()

def _unique_refs(df: pd.DataFrame, col: str) -> pd.Series:
    return df[col].dropna().astype(str).str.strip()

def RSK_GAI_002_count_open_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    excluded_states: Optional[set[str]] = None,
) -> int:
    excluded = {s.lower() for s in (excluded_states or EXCLUDED_STATES_OPEN)}
    df = _read_risk_cards(risk_cards_path, sheet_name)

    for c in (state_col, local_risk_ref_col):
        if c not in df.columns:
            raise ValueError(f"Colonne '{c}' introuvable. Colonnes dispo: {list(df.columns)}")

    open_mask = ~_norm_series(df[state_col]).isin(excluded)
    return int(_unique_refs(df.loc[open_mask], local_risk_ref_col).nunique())

def RSK_GAI_007_count_non_validated_open_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    # périmètre "open"
    state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    excluded_states_open: Optional[set[str]] = None,
    # règles "validé"
    status_col: str = "Status",
    sub_state_col: str = "Sub-State",
    managed_value: str = "Managed",
    respond_value: str = "Respond",
    implementation_value: str = "Implementation",
) -> int:
    """
    RSK-GAI-007 — Nombre de risk cards OPEN non validées.

    Validé si :
    - Status == Managed (peu importe Sub-State)
    OU
    - Status == Respond ET Sub-State == Implementation

    Non validé = (Open distinct Local risk reference) - (Validé distinct Local risk reference) sur le même périmètre Open.
    """
    excluded = {s.lower() for s in (excluded_states_open or EXCLUDED_STATES_OPEN)}

    df = _read_risk_cards(risk_cards_path, sheet_name)

    required = [state_col, local_risk_ref_col, status_col, sub_state_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}. Colonnes dispo: {list(df.columns)}")

    # Scope OPEN (même règle que RSK-GAI-002)
    open_mask = ~_norm_series(df[state_col]).isin(excluded)
    df_open = df.loc[open_mask].copy()

    # Total open (distinct Local risk reference)
    open_refs = _unique_refs(df_open, local_risk_ref_col)
    open_count = int(open_refs.nunique())

    # Validés dans le scope open
    status_norm = _norm_series(df_open[status_col])
    sub_norm = _norm_series(df_open[sub_state_col])

    managed_mask = status_norm == managed_value.strip().lower()
    respond_impl_mask = (status_norm == respond_value.strip().lower()) & (sub_norm == implementation_value.strip().lower())
    validated_mask = managed_mask | respond_impl_mask

    validated_refs = _unique_refs(df_open.loc[validated_mask], local_risk_ref_col)
    validated_count = int(validated_refs.nunique())

    non_validated = open_count - validated_count
    return max(0, int(non_validated))

def write_metrics_to_excel(metrics: list[tuple[str, int]], output_path: Union[str, Path]) -> None:
    pd.DataFrame(metrics, columns=["Indicator", "Value"]).to_excel(output_path, index=False, engine="openpyxl")

def main():
    # ======== À ADAPTER =========
    risk_cards_path = "risk_cards.xlsx"
    risk_cards_sheet = 0  # ou "RiskCards"
    output_path = "resultats_indicateurs.xlsx"
    # ============================

    metrics: list[tuple[str, int]] = []

    # RSK-GAI-002
    metrics.append((
        "RSK-GAI-002",
        RSK_GAI_002_count_open_risk_cards(
            risk_cards_path=risk_cards_path,
            sheet_name=risk_cards_sheet,
            state_col="State",
            local_risk_ref_col="Local risk reference",
        ),
    ))

    # RSK-GAI-007
    metrics.append((
        "RSK-GAI-007",
        RSK_GAI_007_count_non_validated_open_risk_cards(
            risk_cards_path=risk_cards_path,
            sheet_name=risk_cards_sheet,
            state_col="State",
            local_risk_ref_col="Local risk reference",
            status_col="Status",          # adapte si le nom diffère dans ton fichier
            sub_state_col="Sub-State",    # adapte si le nom diffère dans ton fichier
        ),
    ))

    write_metrics_to_excel(metrics, output_path)
    print(f"Fichier généré: {output_path}")

if __name__ == "__main__":
    main()
