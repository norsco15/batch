import pandas as pd
from typing import Union, Optional
from pathlib import Path
from datetime import date

EXCLUDED_STATES_OPEN = {"retired", "cancelled", "closed"}

# =========================
# Helpers
# =========================
def _read_excel(path: Union[str, Path], sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

def _norm_series(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip().str.lower()

def _strip_series(s: pd.Series) -> pd.Series:
    return s.dropna().astype(str).str.strip()

# =========================
# Risk cards: OPEN + VALIDATED sets
# =========================
def get_open_risk_card_refs(
    df_risk: pd.DataFrame,
    state_col: str = "State",
    local_risk_ref_col: str = "Local risk reference",
    excluded_states_open: Optional[set[str]] = None,
) -> set[str]:
    excluded = {s.lower() for s in (excluded_states_open or EXCLUDED_STATES_OPEN)}
    for c in (state_col, local_risk_ref_col):
        if c not in df_risk.columns:
            raise ValueError(f"Colonne '{c}' introuvable (risk cards). Colonnes dispo: {list(df_risk.columns)}")

    open_mask = ~_norm_series(df_risk[state_col]).isin(excluded)
    return set(_strip_series(df_risk.loc[open_mask, local_risk_ref_col]).tolist())

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
    """
    Validé si:
    - Status == Managed
    OU
    - Status == Respond ET Sub-State == Implementation
    Le tout dans le périmètre OPEN (même filtre que RSK-GAI-002).
    """
    required = [state_col, local_risk_ref_col, status_col, sub_state_col]
    missing = [c for c in required if c not in df_risk.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes (risk cards): {missing}. Colonnes dispo: {list(df_risk.columns)}")

    excluded = {s.lower() for s in (excluded_states_open or EXCLUDED_STATES_OPEN)}
    open_mask = ~_norm_series(df_risk[state_col]).isin(excluded)
    df_open = df_risk.loc[open_mask].copy()

    status_norm = _norm_series(df_open[status_col])
    sub_norm = _norm_series(df_open[sub_state_col])

    managed_mask = status_norm == managed_value.strip().lower()
    respond_impl_mask = (status_norm == respond_value.strip().lower()) & (sub_norm == implementation_value.strip().lower())
    validated_mask = managed_mask | respond_impl_mask

    return set(_strip_series(df_open.loc[validated_mask, local_risk_ref_col]).tolist())

# =========================
# RSK-GAI-008
# =========================
def RSK_GAI_008_validated_risk_cards_with_overdue_ipt(
    risk_cards_path: Union[str, Path],
    ipt_path: Union[str, Path],
    risk_cards_sheet: Union[str, int] = 0,
    ipt_sheet: Union[str, int] = 0,
    # risk cards columns
    risk_state_col: str = "State",
    risk_local_ref_col: str = "Local risk reference",
    risk_status_col: str = "Status",
    risk_sub_state_col: str = "Sub-State",
    # ipt columns
    ipt_local_ref_col: str = "Local risk reference",
    ipt_planned_end_date_col: str = "Planned end date",
    # optional: if you still want to keep this as an identifier column check
    ipt_number_col: str = "Number",
    # config
    excluded_states_open: Optional[set[str]] = None,
    today: Optional[date] = None,
) -> int:
    """
    RSK-GAI-008 — Nombre de risk cards VALIDÉES qui ont au moins 1 IPT overdue.

    IPT overdue si (à l’instant T):
      Planned end date < T   (date dépassée)

    Méthode:
    1) Construire l'ensemble des Local risk reference VALIDÉS (dans le scope OPEN).
    2) Dans ipt.xlsx, filtrer les IPT dont Planned end date est dépassée.
    3) Récupérer les Local risk reference correspondants et compter combien sont dans l'ensemble VALIDÉ.
       (count distinct Local risk reference)
    """
    if today is None:
        today = date.today()
    today_ts = pd.Timestamp(today)

    df_risk = _read_excel(risk_cards_path, risk_cards_sheet)
    df_ipt = _read_excel(ipt_path, ipt_sheet)

    # Validate required IPT columns
    required_ipt = [ipt_local_ref_col, ipt_planned_end_date_col]
    missing_ipt = [c for c in required_ipt if c not in df_ipt.columns]
    if missing_ipt:
        raise ValueError(f"Colonnes manquantes (IPT): {missing_ipt}. Colonnes dispo: {list(df_ipt.columns)}")

    # (Optionnel) vérifier Number si tu veux t'assurer qu'il existe
    if ipt_number_col and ipt_number_col not in df_ipt.columns:
        # On ne bloque pas car on n'en a pas besoin pour le calcul.
        pass

    # 1) set des risk cards validées (scope open)
    validated_refs = get_validated_open_risk_card_refs(
        df_risk=df_risk,
        state_col=risk_state_col,
        local_risk_ref_col=risk_local_ref_col,
        excluded_states_open=excluded_states_open,
        status_col=risk_status_col,
        sub_state_col=risk_sub_state_col,
    )

    # 2) IPT overdue
    planned_end = pd.to_datetime(df_ipt[ipt_planned_end_date_col], errors="coerce")
    overdue_mask = planned_end.notna() & (planned_end < today_ts)

    overdue_refs = set(_strip_series(df_ipt.loc[overdue_mask, ipt_local_ref_col]).tolist())

    # 3) intersection
    validated_with_overdue = validated_refs.intersection(overdue_refs)

    return int(len(validated_with_overdue))

# =========================
# Output writer + main
# =========================
def write_metrics_to_excel(metrics: list[tuple[str, int]], output_path: Union[str, Path]) -> None:
    pd.DataFrame(metrics, columns=["Indicator", "Value"]).to_excel(output_path, index=False, engine="openpyxl")

def main():
    # ======== À ADAPTER =========
    risk_cards_path = "risk_cards.xlsx"
    ipt_path = "ipt.xlsx"
    risk_cards_sheet = 0   # ou "RiskCards"
    ipt_sheet = 0          # ou "IPT"
    output_path = "resultats_indicateurs.xlsx"

    # Si tu veux figer "instant T" (ex: 2026-01-28):
    # from datetime import date
    # today = date(2026, 1, 28)
    today = None
    # ============================

    metrics: list[tuple[str, int]] = []

    metrics.append((
        "RSK-GAI-008",
        RSK_GAI_008_validated_risk_cards_with_overdue_ipt(
            risk_cards_path=risk_cards_path,
            ipt_path=ipt_path,
            risk_cards_sheet=risk_cards_sheet,
            ipt_sheet=ipt_sheet,
            risk_state_col="State",
            risk_local_ref_col="Local risk reference",
            risk_status_col="Status",
            risk_sub_state_col="Sub-State",
            ipt_local_ref_col="Local risk reference",
            ipt_planned_end_date_col="Planned end date",
            ipt_number_col="Number",
            today=today,
        ),
    ))

    write_metrics_to_excel(metrics, output_path)
    print(f"Fichier généré: {output_path}")

if __name__ == "__main__":
    main()
