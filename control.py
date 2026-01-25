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
    OPEN = State not in {Retired, Cancelled, Closed}
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

    refs_norm = refs.astype(str).str.strip()
    return int(refs_norm.nunique())

def write_metrics_to_excel(metrics: list[tuple[str, int]], output_path: Union[str, Path]) -> None:
    """
    Écrit les métriques dans un fichier Excel avec 2 colonnes :
    - Indicator
    - Value
    """
    df_out = pd.DataFrame(metrics, columns=["Indicator", "Value"])
    df_out.to_excel(output_path, index=False, engine="openpyxl")

def main():
    # ======== À ADAPTER =========
    risk_cards_path = "risk_cards.xlsx"
    risk_cards_sheet = 0  # ou "RiskCards"
    output_path = "resultats_indicateurs.xlsx"
    # ============================

    metrics: list[tuple[str, int]] = []

    # --- Indicateur RSK_GAI_002 ---
    rsk_gai_002 = RSK_GAI_002_count_open_risk_cards(
        risk_cards_path=risk_cards_path,
        sheet_name=risk_cards_sheet,
        state_col="State",
        local_risk_ref_col="Local risk reference",
    )
    metrics.append(("RSK_GAI_002", rsk_gai_002))

    # (plus tard: ajouter d'autres indicateurs ici, puis append dans metrics)

    write_metrics_to_excel(metrics, output_path)
    print(f"Fichier généré: {output_path}")

if __name__ == "__main__":
    main()
