import pandas as pd
from typing import Union, Optional
from pathlib import Path

EXCLUDED_STATES_OPEN = {"retired", "cancelled", "closed"}

def _read_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
) -> pd.DataFrame:
    return pd.read_excel(risk_cards_path, sheet_name=sheet_name, engine="openpyxl")

def _open_mask(
    df: pd.DataFrame,
    state_col: str,
    excluded_states: set[str],
) -> pd.Series:
    state_norm = df[state_col].astype(str).str.strip().str.lower()
    return ~state_norm.isin(excluded_states)

def RSK_GAI_002_count_open_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    excluded_states: Optional[set[str]] = None,
    dropna_refs: bool = True,
) -> int:
    excluded = {s.lower() for s in (excluded_states or EXCLUDED_STATES_OPEN)}

    df = _read_risk_cards(risk_cards_path, sheet_name)

    missing = [c for c in [state_col, local_risk_ref_col] if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}. Colonnes dispo: {list(df.columns)}")

    open_mask = _open_mask(df, state_col, excluded)

    refs = df.loc[open_mask, local_risk_ref_col]
    if dropna_refs:
        refs = refs.dropna()

    refs_norm = refs.astype(str).str.strip()
    return int(refs_norm.nunique())

def RSK_GAI_003_count_open_major_extreme_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    residual_risk_level_col: str = "Residual risk level",
    included_levels: Optional[set[str]] = None,
    excluded_states: Optional[set[str]] = None,
    dropna_refs: bool = True,
) -> int:
    """
    RSK_GAI_003 — Nombre de risk cards OPEN (même périmètre que RSK_GAI_002)
    dont 'Residual risk level' est Major ou Extreme.

    On compte le nombre de 'Local risk reference' DISTINCTS.
    Valeurs attendues par défaut : '3 - Major' et '4 - Extreme'
    """
    excluded = {s.lower() for s in (excluded_states or EXCLUDED_STATES_OPEN)}
    levels = included_levels or {"3 - Major", "4 - Extreme"}

    df = _read_risk_cards(risk_cards_path, sheet_name)

    required = [state_col, local_risk_ref_col, residual_risk_level_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}. Colonnes dispo: {list(df.columns)}")

    open_mask = _open_mask(df, state_col, excluded)

    # Filtre sur levels (normalisation trim pour éviter les soucis d'espaces)
    rr_norm = df[residual_risk_level_col].astype(str).str.strip()
    level_mask = rr_norm.isin({str(v).strip() for v in levels})

    scoped = df.loc[open_mask & level_mask, local_risk_ref_col]
    if dropna_refs:
        scoped = scoped.dropna()

    scoped_norm = scoped.astype(str).str.strip()
    return int(scoped_norm.nunique())

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

    # RSK_GAI_002
    metrics.append((
        "RSK_GAI_002",
        RSK_GAI_002_count_open_risk_cards(
            risk_cards_path=risk_cards_path,
            sheet_name=risk_cards_sheet,
            state_col="State",
            local_risk_ref_col="Local risk reference",
        ),
    ))

    # RSK_GAI_003
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

    write_metrics_to_excel(metrics, output_path)
    print(f"Fichier généré: {output_path}")

if __name__ == "__main__":
    main()
