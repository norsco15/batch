import pandas as pd
from typing import Union, Optional
from pathlib import Path

EXCLUDED_STATES_OPEN = {"retired", "cancelled", "closed"}

def RSK_GAI_002_count_open_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    excluded_states: Optional[set[str]] = None,
    dropna_refs: bool = True,
) -> int:
    """
    RSK_GAI_002 — Nombre de risk cards OPEN (comptées par 'Local risk reference' unique).

    Contexte :
    - Dans le fichier, 'Local risk reference' peut apparaître en doublon (une risk card peut pointer vers plusieurs Risk ID).
    - On veut compter le nombre de risk cards ouvertes => nombre de 'Local risk reference' DISTINCTS
      dont le State n'est pas dans: Retired, Cancelled, Closed.
    """
    excluded = {s.lower() for s in (excluded_states or EXCLUDED_STATES_OPEN)}

    df = pd.read_excel(risk_cards_path, sheet_name=sheet_name, engine="openpyxl")

    missing = [c for c in [state_col, local_risk_ref_col] if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}. Colonnes dispo: {list(df.columns)}")

    state_norm = df[state_col].astype(str).str.strip().str.lower()
    open_mask = ~state_norm.isin(excluded)

    refs = df.loc[open_mask, local_risk_ref_col]
    if dropna_refs:
        refs = refs.dropna()

    # Normalisation légère (trim) pour éviter les doublons dus aux espaces
    refs_norm = refs.astype(str).str.strip()

    return int(refs_norm.nunique())

def main():
    # ======== À ADAPTER =========
    risk_cards_path = "risk_cards.xlsx"
    sheet_name = 0  # ou "RiskCards"
    state_col = "State"
    local_risk_ref_col = "Local risk reference"
    # ============================

    rsk_gai_002 = RSK_GAI_002_count_open_risk_cards(
        risk_cards_path=risk_cards_path,
        sheet_name=sheet_name,
        state_col=state_col,
        local_risk_ref_col=local_risk_ref_col,
    )

    print(f"RSK_GAI_002 (Open risk cards, distinct '{local_risk_ref_col}') = {rsk_gai_002}")

if __name__ == "__main__":
    main()
