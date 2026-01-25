import pandas as pd
from typing import Union, Optional
from pathlib import Path

EXCLUDED_STATES_OPEN = {"retired", "cancelled", "closed"}

def RSK_GAI_002_count_open_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    state_col: str = "State",
    excluded_states: Optional[set[str]] = None,
) -> int:
    """
    RSK_GAI_002 — Nombre de risk cards OPEN.
    Une risk card est considérée OPEN si son 'State' n'est pas dans: Retired, Cancelled, Closed.
    """
    excluded = {s.lower() for s in (excluded_states or EXCLUDED_STATES_OPEN)}

    df = pd.read_excel(risk_cards_path, sheet_name=sheet_name, engine="openpyxl")

    if state_col not in df.columns:
        raise ValueError(
            f"Colonne '{state_col}' introuvable. Colonnes disponibles: {list(df.columns)}"
        )

    state_norm = df[state_col].astype(str).str.strip().str.lower()
    open_mask = ~state_norm.isin(excluded)

    return int(open_mask.sum())

def main():
    # ======== À ADAPTER =========
    risk_cards_path = "risk_cards.xlsx"
    sheet_name = 0            # ou "RiskCards"
    state_col = "State"
    # ============================

    rsk_gai_002 = RSK_GAI_002_count_open_risk_cards(
        risk_cards_path=risk_cards_path,
        sheet_name=sheet_name,
        state_col=state_col,
    )

    print(f"RSK_GAI_002 (Open risk cards) = {rsk_gai_002}")

if __name__ == "__main__":
    main()
