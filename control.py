import pandas as pd
from typing import Union, Optional
from pathlib import Path

def _read_excel(path: Union[str, Path], sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

def _norm_series(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip().str.lower()

def _strip_series(s: pd.Series) -> pd.Series:
    return s.dropna().astype(str).str.strip()

def RSK_GPI_007_count_major_risk_cards_with_ipt_postponed_18m(
    risk_cards_path: Union[str, Path],
    ipt_path: Union[str, Path],
    risk_cards_sheet: Union[str, int] = 0,
    ipt_sheet: Union[str, int] = 0,
    # risk cards columns
    local_risk_ref_col: str = "Local risk reference",
    residual_risk_level_col: str = "Residual risk level",
    major_value: str = "3 - Major",
    # ipt columns
    ipt_local_risk_ref_col: str = "Local risk reference",
    initial_due_date_col: str = "Initial due Date",
    planned_end_date_col: str = "Planned end date",
) -> int:
    """
    RSK-GPI-007 — Nombre de risk cards MAJOR qui ont au moins 1 IPT "postponé" de plus de 18 mois.

    Règle IPT postponé >18 mois:
      Planned end date > Initial due Date + 18 mois

    Sortie:
      Nombre de 'Local risk reference' DISTINCTS (côté risk cards)
      appartenant à (Major risk cards) ∩ (risk cards ayant >=1 IPT postponé >18 mois).
    """
    df_risk = _read_excel(risk_cards_path, risk_cards_sheet)
    df_ipt = _read_excel(ipt_path, ipt_sheet)

    # --- checks ---
    for c in (local_risk_ref_col, residual_risk_level_col):
        if c not in df_risk.columns:
            raise ValueError(f"Colonne '{c}' introuvable (risk cards). Colonnes dispo: {list(df_risk.columns)}")

    for c in (ipt_local_risk_ref_col, initial_due_date_col, planned_end_date_col):
        if c not in df_ipt.columns:
            raise ValueError(f"Colonne '{c}' introuvable (IPT). Colonnes dispo: {list(df_ipt.columns)}")

    # --- 1) set des risk cards Major ---
    rr_norm = _norm_series(df_risk[residual_risk_level_col])
    major_mask = rr_norm == major_value.strip().lower()
    major_refs = set(_strip_series(df_risk.loc[major_mask, local_risk_ref_col]).tolist())

    # --- 2) set des risk cards ayant >=1 IPT postponé >18 mois ---
    init_due = pd.to_datetime(df_ipt[initial_due_date_col], errors="coerce")
    planned_end = pd.to_datetime(df_ipt[planned_end_date_col], errors="coerce")

    # postponé > 18 mois  <=> planned_end > init_due + 18 months
    threshold = init_due + pd.DateOffset(months=18)
    postponed_mask = init_due.notna() & planned_end.notna() & (planned_end > threshold)

    postponed_refs = set(_strip_series(df_ipt.loc[postponed_mask, ipt_local_risk_ref_col]).tolist())

    # --- 3) intersection ---
    major_with_postponed = major_refs.intersection(postponed_refs)
    return int(len(major_with_postponed))


# -------------------------
# Exemple d’intégration dans ton main + fichier résultats
# -------------------------
def write_metrics_to_excel(metrics: list[tuple[str, int]], output_path: Union[str, Path]) -> None:
    pd.DataFrame(metrics, columns=["Indicator", "Value"]).to_excel(output_path, index=False, engine="openpyxl")

def main():
    # ======== À ADAPTER =========
    risk_cards_path = "risk_cards.xlsx"
    ipt_path = "ipt.xlsx"
    risk_cards_sheet = 0
    ipt_sheet = 0
    output_path = "resultats_indicateurs.xlsx"
    # ============================

    metrics: list[tuple[str, int]] = []

    metrics.append((
        "RSK-GPI-007",
        RSK_GPI_007_count_major_risk_cards_with_ipt_postponed_18m(
            risk_cards_path=risk_cards_path,
            ipt_path=ipt_path,
            risk_cards_sheet=risk_cards_sheet,
            ipt_sheet=ipt_sheet,
            residual_risk_level_col="Residual risk level",
            major_value="3 - Major",
            initial_due_date_col="Initial due Date",
            planned_end_date_col="Planned end date",
            ipt_local_risk_ref_col="Local risk reference",
            local_risk_ref_col="Local risk reference",
        ),
    ))

    write_metrics_to_excel(metrics, output_path)
    print(f"Fichier généré: {output_path}")

if __name__ == "__main__":
    main()
