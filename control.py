import pandas as pd
from typing import Union, Optional
from pathlib import Path
from datetime import date

EXCLUDED_STATES_OPEN = {"retired", "cancelled", "closed"}

def _read_risk_cards(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
) -> pd.DataFrame:
    return pd.read_excel(risk_cards_path, sheet_name=sheet_name, engine="openpyxl")

def _norm_series(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip().str.lower()

def _count_state_in_month(
    df: pd.DataFrame,
    state_col: str,
    target_state: str,
    date_col: str,
    year: int,
    month: int,
) -> int:
    """
    Compte le nombre de lignes dont:
    - state_col == target_state
    - date_col est dans (year, month)
    """
    if state_col not in df.columns:
        raise ValueError(f"Colonne '{state_col}' introuvable. Colonnes dispo: {list(df.columns)}")
    if date_col not in df.columns:
        raise ValueError(f"Colonne '{date_col}' introuvable. Colonnes dispo: {list(df.columns)}")

    state_norm = _norm_series(df[state_col])
    mask_state = state_norm == target_state.strip().lower()

    # Convertit la colonne date (Excel peut donner datetime/str/float)
    d = pd.to_datetime(df[date_col], errors="coerce")
    mask_month = (d.dt.year == year) & (d.dt.month == month)

    return int((mask_state & mask_month).sum())

def RSK_GAI_006_monthly_closed_retired(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    state_col: str = "State (Evaluation Status)",
    retired_state: str = "Retired",
    retired_date_col: str = "Risk retirement date",
    closed_state: str = "Closed",
    closed_date_col: str = "Risk closure date",
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> int:
    """
    RSK-GAI-006 — Nombre de monthly risk cards Closed/Retired.

    Règle:
    - Retired: compter les lignes avec State=Retired ET 'Risk retirement date' dans le mois courant.
    - Closed:  compter les lignes avec State=Closed  ET 'Risk closure date'   dans le mois courant.
    - Retourner la somme des deux.
    """
    df = _read_risk_cards(risk_cards_path, sheet_name)

    if year is None or month is None:
        today = date.today()
        year = today.year
        month = today.month

    retired_count = _count_state_in_month(
        df=df,
        state_col=state_col,
        target_state=retired_state,
        date_col=retired_date_col,
        year=year,
        month=month,
    )

    closed_count = _count_state_in_month(
        df=df,
        state_col=state_col,
        target_state=closed_state,
        date_col=closed_date_col,
        year=year,
        month=month,
    )

    return retired_count + closed_count

def write_metrics_to_excel(metrics: list[tuple[str, int]], output_path: Union[str, Path]) -> None:
    df_out = pd.DataFrame(metrics, columns=["Indicator", "Value"])
    df_out.to_excel(output_path, index=False, engine="openpyxl")

def main():
    # ======== À ADAPTER =========
    risk_cards_path = "risk_cards.xlsx"
    risk_cards_sheet = 0  # ou "RiskCards"
    output_path = "resultats_indicateurs.xlsx"

    # Période "mois en cours" : si tu veux forcer Janvier 2026 par ex:
    # year, month = 2026, 1
    year, month = None, None
    # ============================

    metrics: list[tuple[str, int]] = []

    # Exemple: on ne remet pas ici RSK_GAI_002/003 si tu les as déjà dans ton script
    metrics.append((
        "RSK-GAI-006",
        RSK_GAI_006_monthly_closed_retired(
            risk_cards_path=risk_cards_path,
            sheet_name=risk_cards_sheet,
            state_col="State (Evaluation Status)",
            retired_date_col="Risk retirement date",
            closed_date_col="Risk closure date",
            year=year,
            month=month,
        ),
    ))

    write_metrics_to_excel(metrics, output_path)
    print(f"Fichier généré: {output_path}")

if __name__ == "__main__":
    main()
