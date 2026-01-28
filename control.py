import pandas as pd
from typing import Union, Optional
from pathlib import Path
from datetime import date

def _read_excel(path: Union[str, Path], sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

def _norm_series(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip().str.lower()

def _strip_series(s: pd.Series) -> pd.Series:
    return s.dropna().astype(str).str.strip()

def _count_major_extreme_response_recorded_gt_months(
    df_risk: pd.DataFrame,
    local_risk_ref_col: str,
    residual_risk_level_col: str,
    response_col: str,
    recorded_date_col: str,
    responses: set[str],
    months: int,
    major_extreme_values: Optional[set[str]] = None,
    asof: Optional[date] = None,
) -> int:
    """
    Compte le nombre de Local risk reference DISTINCTS tels que:
    - Residual risk level ∈ {Major, Extreme}
    - Response ∈ responses
    - Recorded date <= (asof - months)
    """
    if asof is None:
        asof = date.today()
    asof_ts = pd.Timestamp(asof)
    threshold = asof_ts - pd.DateOffset(months=months)

    major_extreme = major_extreme_values or {"3 - Major", "4 - Extreme"}

    required = [local_risk_ref_col, residual_risk_level_col, response_col, recorded_date_col]
    missing = [c for c in required if c not in df_risk.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes (risk cards): {missing}. Colonnes dispo: {list(df_risk.columns)}")

    rr_norm = _norm_series(df_risk[residual_risk_level_col])
    level_mask = rr_norm.isin({v.strip().lower() for v in major_extreme})

    resp_norm = _norm_series(df_risk[response_col])
    resp_mask = resp_norm.isin({r.strip().lower() for r in responses})

    rec = pd.to_datetime(df_risk[recorded_date_col], errors="coerce")
    rec_mask = rec.notna() & (rec <= threshold)

    refs = _strip_series(df_risk.loc[level_mask & resp_mask & rec_mask, local_risk_ref_col])
    return int(refs.nunique())

def RSK_GAI_009_count_major_extreme_accept_recorded_gt_24m(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    local_risk_ref_col: str = "Local risk reference",
    residual_risk_level_col: str = "Residual risk level",
    response_col: str = "Reponse",
    recorded_date_col: str = "Recorded date",
    asof: Optional[date] = None,
) -> int:
    """
    RSK-GAI-009 — Major/Extreme + Reponse=Accept + Recorded date > 24 mois (recorded since more than 24 months).
    """
    df = _read_excel(risk_cards_path, sheet_name)
    return _count_major_extreme_response_recorded_gt_months(
        df_risk=df,
        local_risk_ref_col=local_risk_ref_col,
        residual_risk_level_col=residual_risk_level_col,
        response_col=response_col,
        recorded_date_col=recorded_date_col,
        responses={"Accept"},
        months=24,
        asof=asof,
    )

def RSK_GAI_0010_count_major_extreme_mitigate_recorded_gt_24m(
    risk_cards_path: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    local_risk_ref_col: str = "Local risk reference",
    residual_risk_level_col: str = "Residual risk level",
    response_col: str = "Reponse",
    recorded_date_col: str = "Recorded date",
    asof: Optional[date] = None,
) -> int:
    """
    RSK-GAI-0010 — Major/Extreme + Reponse=Mitigate + Recorded date > 24 mois (recorded since more than 24 months).
    """
    df = _read_excel(risk_cards_path, sheet_name)
    return _count_major_extreme_response_recorded_gt_months(
        df_risk=df,
        local_risk_ref_col=local_risk_ref_col,
        residual_risk_level_col=residual_risk_level_col,
        response_col=response_col,
        recorded_date_col=recorded_date_col,
        responses={"Mitigate"},
        months=24,
        asof=asof,
    )

# --------- output + main ----------
def write_metrics_to_excel(metrics: list[tuple[str, int]], output_path: Union[str, Path]) -> None:
    pd.DataFrame(metrics, columns=["Indicator", "Value"]).to_excel(output_path, index=False, engine="openpyxl")

def main():
    # ======== À ADAPTER =========
    risk_cards_path = "risk_cards.xlsx"
    risk_cards_sheet = 0  # ou "RiskCards"
    output_path = "resultats_indicateurs.xlsx"

    # Si tu veux figer l’instant T (ex: 2026-01-28):
    # asof = date(2026, 1, 28)
    asof = None
    # ============================

    metrics: list[tuple[str, int]] = []

    metrics.append((
        "RSK-GAI-009",
        RSK_GAI_009_count_major_extreme_accept_recorded_gt_24m(
            risk_cards_path=risk_cards_path,
            sheet_name=risk_cards_sheet,
            response_col="Reponse",
            recorded_date_col="Recorded date",
            residual_risk_level_col="Residual risk level",
            asof=asof,
        ),
    ))

    metrics.append((
        "RSK-GAI-0010",
        RSK_GAI_0010_count_major_extreme_mitigate_recorded_gt_24m(
            risk_cards_path=risk_cards_path,
            sheet_name=risk_cards_sheet,
            response_col="Reponse",
            recorded_date_col="Recorded date",
            residual_risk_level_col="Residual risk level",
            asof=asof,
        ),
    ))

    write_metrics_to_excel(metrics, output_path)
    print(f"Fichier généré: {output_path}")

if __name__ == "__main__":
    main()
