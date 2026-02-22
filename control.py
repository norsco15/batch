import re
import calendar
from datetime import datetime
import pandas as pd


# =========================
# Utils
# =========================
def norm_str(x) -> str:
    """Normalize to stripped string; empty string if NaN/None."""
    if pd.isna(x):
        return ""
    return str(x).strip()

def is_blank(x) -> bool:
    return norm_str(x) == ""

def first_digit_1_to_4(s: str):
    """Extract first digit 1..4 found in the string. Return int or None."""
    s = norm_str(s)
    m = re.search(r"[1-4]", s)
    return int(m.group(0)) if m else None

def parse_date_any(x):
    """
    Parse date from Excel cell:
    - if it's already datetime/date -> ok
    - if it's string 'yyyy-MM-dd' -> parse
    - else -> try pandas parser
    Return pandas.Timestamp or None.
    """
    if pd.isna(x):
        return None
    if isinstance(x, (datetime, pd.Timestamp)):
        return pd.Timestamp(x).normalize()
    s = norm_str(x)
    if not s:
        return None
    # strict first: yyyy-MM-dd
    try:
        return pd.to_datetime(s, format="%Y-%m-%d", errors="raise").normalize()
    except Exception:
        # fallback (Excel weird formats)
        try:
            return pd.to_datetime(s, errors="coerce").normalize()
        except Exception:
            return None

def last_day_of_month(ts: pd.Timestamp) -> int:
    return calendar.monthrange(ts.year, ts.month)[1]


# =========================
# Reporting
# =========================
def add_failure(failures, rule_id, severity, row_idx, row_key, column, value, recommendation):
    failures.append({
        "rule_id": rule_id,
        "severity": severity,
        "row_index": row_idx,
        "row_key": row_key,          # helpful identifier (Risk ID or Local Risk Reference)
        "column": column,
        "value": value,
        "recommendation": recommendation
    })

def choose_row_key(row):
    # Prefer Risk ID, else Local Risk Reference, else empty
    rid = norm_str(row.get("Risk ID", ""))
    rlr = norm_str(row.get("Local Risk Reference", ""))
    return rid or rlr or ""


# =========================
# Rules
# =========================
def run_quality_checks(df: pd.DataFrame):
    failures = []

    # Safety: ensure expected columns exist (we'll still run what we can)
    expected_cols = [
        "Risk ID",
        "Local Risk Reference",
        "Title",
        "Residual risk level",
        "Remediation Count",
        "Response",
        "Business organization owning the risk",
        "Business entity (Bus. Org. owning the risk)",
        "Business entity (IT Org. managing the risk)",
        "IT organization managing the risk",
        "Risk Owner/Sponsor",
        "Risk Category",
        "Topic Sub-Category",
        "Risk statement level 3",
        "Recorded date",
        "Identification date",
        "Latest review comments",
        "Description",
        "Target residual risk level",
        "Next review date",
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        # global "schema" failures: one per missing column (not per row)
        for c in missing:
            add_failure(
                failures,
                rule_id="SCHEMA_MISSING_COLUMN",
                severity="BLOCKER",
                row_idx=None,
                row_key="",
                column=c,
                value="(missing column)",
                recommendation=f"Ajouter la colonne '{c}' dans l'extraction ou corriger le nom exact de la colonne."
            )

    # Constants / patterns
    BP2I_MAIN = "BP2I - BNP PARIBAS PARTNERS FOR INNOVATION"

    # Business org owning the risk:
    # - either exactly BP2I_MAIN
    # - OR starts with "BP2I " then next token endswith "A"
    # e.g. "BP2I CI22A - EMEA RISK" ok, "BP2I CI22B - ..." not ok
    business_org_regex = re.compile(r"^BP2I\s+(\S+)", re.IGNORECASE)

    # IT org managing the risk must be either "BP2I CI22B ..." or "BP2I CI23B ..."
    it_org_regex = re.compile(r"^BP2I\s+CI(22B|23B)\b", re.IGNORECASE)

    # Description must contain those sections in order
    # "Context ... Vulnerabilities ... Threat ... Impacted Assets ... Annual Review ..."
    desc_sections = ["Context", "Vulnerabilities", "Threat", "Impacted Assets", "Annual Review"]
    desc_pattern = re.compile(
        r"Context[\s\S]*Vulnerabilities[\s\S]*Threat[\s\S]*Impacted Assets[\s\S]*Annual Review",
        re.IGNORECASE
    )

    # Iterate rows
    for idx, row in df.iterrows():
        row_key = choose_row_key(row)

        # 1) Risk ID -> not blank + starts RK
        col = "Risk ID"
        if col in df.columns:
            v = norm_str(row[col])
            if not v:
                add_failure(failures, "RISK_ID_NOT_BLANK", "BLOCKER", idx, row_key, col, v,
                            "Renseigner un Risk ID non vide (ex: RKxxxx).")
            elif not v.startswith("RK"):
                add_failure(failures, "RISK_ID_STARTS_RK", "BLOCKER", idx, row_key, col, v,
                            "Le Risk ID doit commencer par 'RK' (ex: RK12345).")

        # 2) Local Risk Reference -> not blank + starts RL
        col = "Local Risk Reference"
        if col in df.columns:
            v = norm_str(row[col])
            if not v:
                add_failure(failures, "LOCAL_RISK_REF_NOT_BLANK", "BLOCKER", idx, row_key, col, v,
                            "Renseigner une Local Risk Reference non vide (ex: RLxxxx).")
            elif not v.startswith("RL"):
                add_failure(failures, "LOCAL_RISK_REF_STARTS_RL", "BLOCKER", idx, row_key, col, v,
                            "La Local Risk Reference doit commencer par 'RL' (ex: RL123).")

        # 3) Title -> not blank + starts with BP2I-RL{LocalRiskRef}
        col = "Title"
        if col in df.columns:
            title = norm_str(row[col])
            lrr = norm_str(row.get("Local Risk Reference", ""))
            if not title:
                add_failure(failures, "TITLE_NOT_BLANK", "BLOCKER", idx, row_key, col, title,
                            "Renseigner un Title non vide.")
            else:
                if lrr:
                    expected_prefix = f"BP2I-{lrr}"
                    if not title.startswith(expected_prefix):
                        add_failure(
                            failures, "TITLE_PREFIX_BP2I_RL", "MAJOR", idx, row_key, col, title,
                            f"Le Title doit commencer par '{expected_prefix}...' (ex: {expected_prefix} - <suite>)."
                        )
                else:
                    # Local risk ref empty already flagged; still provide guidance
                    if not title.startswith("BP2I-RL"):
                        add_failure(
                            failures, "TITLE_STARTS_BP2I_RL", "MAJOR", idx, row_key, col, title,
                            "Le Title doit commencer par 'BP2I-RL...' (et idéalement BP2I-{Local Risk Reference})."
                        )

        # 4) Residual risk level -> not blank
        col = "Residual risk level"
        if col in df.columns:
            v = norm_str(row[col])
            if not v:
                add_failure(failures, "RESIDUAL_RISK_LEVEL_NOT_BLANK", "BLOCKER", idx, row_key, col, v,
                            "Renseigner le Residual risk level (ex: 1 - ..., 2 - ...).")

        # 5) Remediation Count -> if Response == 'Accept' then must be 0
        col_rc = "Remediation Count"
        col_resp = "Response"
        if col_rc in df.columns and col_resp in df.columns:
            resp = norm_str(row[col_resp])
            rc_raw = row[col_rc]
            rc_str = norm_str(rc_raw)
            # parse remediation count numeric if possible
            rc_val = None
            if rc_str:
                try:
                    rc_val = int(float(rc_str))
                except Exception:
                    rc_val = None

            if resp == "Accept":
                if rc_val is None:
                    add_failure(
                        failures, "REMEDIATION_COUNT_NUMERIC", "MAJOR", idx, row_key, col_rc, rc_str,
                        "Remediation Count doit être numérique; pour Response='Accept', il doit être 0."
                    )
                elif rc_val != 0:
                    add_failure(
                        failures, "REMEDIATION_COUNT_ACCEPT_ZERO", "MAJOR", idx, row_key, col_rc, rc_val,
                        "Si Response='Accept', Remediation Count doit être 0. Mettre 0 ou corriger la Response."
                    )

        # 6) Business organization owning the risk -> BP2I_MAIN OR BP2I <tokenEndingWithA> ...
        col = "Business organization owning the risk"
        if col in df.columns:
            v = norm_str(row[col])
            if not v:
                add_failure(failures, "BUS_ORG_OWNING_NOT_BLANK", "BLOCKER", idx, row_key, col, v,
                            "Renseigner la Business organization owning the risk.")
            else:
                if v == BP2I_MAIN:
                    pass
                else:
                    m = business_org_regex.match(v)
                    if not m:
                        add_failure(
                            failures, "BUS_ORG_OWNING_FORMAT", "MAJOR", idx, row_key, col, v,
                            "Doit être 'BP2I - BNP PARIBAS PARTNERS FOR INNOVATION' OU commencer par 'BP2I <codeA> ...' (le mot après BP2I doit finir par 'A')."
                        )
                    else:
                        token = m.group(1)
                        if not token.upper().endswith("A"):
                            add_failure(
                                failures, "BUS_ORG_OWNING_TOKEN_ENDS_A", "MAJOR", idx, row_key, col, v,
                                "Le mot suivant 'BP2I' doit finir par 'A' (ex: BP2I CI22A - ...)."
                            )

        # 7) Business entity (Bus. Org. owning the risk) -> not blank + equals BP2I_MAIN
        col = "Business entity (Bus. Org. owning the risk)"
        if col in df.columns:
            v = norm_str(row[col])
            if not v:
                add_failure(failures, "BUS_ENTITY_OWNING_NOT_BLANK", "BLOCKER", idx, row_key, col, v,
                            f"Renseigner '{BP2I_MAIN}'.")
            elif v != BP2I_MAIN:
                add_failure(failures, "BUS_ENTITY_OWNING_EQUALS_BP2I", "MAJOR", idx, row_key, col, v,
                            f"Mettre exactement '{BP2I_MAIN}'.")

        # 8) Business entity (IT Org. managing the risk) -> not blank + equals BP2I_MAIN
        col = "Business entity (IT Org. managing the risk)"
        if col in df.columns:
            v = norm_str(row[col])
            if not v:
                add_failure(failures, "BUS_ENTITY_IT_NOT_BLANK", "BLOCKER", idx, row_key, col, v,
                            f"Renseigner '{BP2I_MAIN}'.")
            elif v != BP2I_MAIN:
                add_failure(failures, "BUS_ENTITY_IT_EQUALS_BP2I", "MAJOR", idx, row_key, col, v,
                            f"Mettre exactement '{BP2I_MAIN}'.")

        # 9) IT organization managing the risk -> not blank + starts BP2I CI22B... or BP2I CI23B...
        col = "IT organization managing the risk"
        if col in df.columns:
            v = norm_str(row[col])
            if not v:
                add_failure(failures, "IT_ORG_MANAGING_NOT_BLANK", "BLOCKER", idx, row_key, col, v,
                            "Renseigner IT organization managing the risk (ex: BP2I CI22B ... ou BP2I CI23B ...).")
            elif not it_org_regex.match(v):
                add_failure(
                    failures, "IT_ORG_MANAGING_ALLOWED_PREFIX", "MAJOR", idx, row_key, col, v,
                    "Doit commencer par 'BP2I CI22B' ou 'BP2I CI23B' (puis le reste peut suivre)."
                )

        # 10) Risk Owner/Sponsor -> not blank
        col = "Risk Owner/Sponsor"
        if col in df.columns and is_blank(row[col]):
            add_failure(failures, "RISK_OWNER_NOT_BLANK", "BLOCKER", idx, row_key, col, norm_str(row[col]),
                        "Renseigner le Risk Owner/Sponsor.")

        # 11) Risk Category -> not blank
        col = "Risk Category"
        if col in df.columns and is_blank(row[col]):
            add_failure(failures, "RISK_CATEGORY_NOT_BLANK", "BLOCKER", idx, row_key, col, norm_str(row[col]),
                        "Renseigner le Risk Category.")

        # 12) Topic Sub-Category -> not blank
        col = "Topic Sub-Category"
        if col in df.columns and is_blank(row[col]):
            add_failure(failures, "TOPIC_SUBCATEGORY_NOT_BLANK", "BLOCKER", idx, row_key, col, norm_str(row[col]),
                        "Renseigner le Topic Sub-Category.")

        # 13) Risk statement level 3 -> not blank
        col = "Risk statement level 3"
        if col in df.columns and is_blank(row[col]):
            add_failure(failures, "RISK_STATEMENT_L3_NOT_BLANK", "BLOCKER", idx, row_key, col, norm_str(row[col]),
                        "Renseigner le Risk statement level 3.")

        # 14) Recorded date -> not blank
        col = "Recorded date"
        if col in df.columns:
            dt = parse_date_any(row[col])
            if dt is None:
                add_failure(failures, "RECORDED_DATE_NOT_BLANK_OR_VALID", "BLOCKER", idx, row_key, col, norm_str(row[col]),
                            "Renseigner une date valide pour Recorded date.")

        # 15) Identification date -> not blank
        col = "Identification date"
        if col in df.columns:
            dt = parse_date_any(row[col])
            if dt is None:
                add_failure(failures, "IDENTIFICATION_DATE_NOT_BLANK_OR_VALID", "BLOCKER", idx, row_key, col, norm_str(row[col]),
                            "Renseigner une date valide pour Identification date.")

        # 16) Latest review comments -> not blank
        col = "Latest review comments"
        if col in df.columns and is_blank(row[col]):
            add_failure(failures, "LATEST_REVIEW_COMMENTS_NOT_BLANK", "MAJOR", idx, row_key, col, norm_str(row[col]),
                        "Renseigner Latest review comments (commentaire de revue).")

        # 17) Description -> not blank + contains sections in order
        col = "Description"
        if col in df.columns:
            v = norm_str(row[col])
            if not v:
                add_failure(failures, "DESCRIPTION_NOT_BLANK", "BLOCKER", idx, row_key, col, v,
                            "Renseigner la Description.")
            else:
                if not desc_pattern.search(v):
                    add_failure(
                        failures, "DESCRIPTION_SECTION_PATTERN", "MAJOR", idx, row_key, col, v[:200] + ("..." if len(v) > 200 else ""),
                        "La Description doit contenir, dans l’ordre : 'Context', 'Vulnerabilities', 'Threat', 'Impacted Assets', 'Annual Review'. (Même si le texte entre sections est libre.)"
                    )

        # 18) Target residual risk level -> not blank + if Response == Mitigate then target < residual
        col_target = "Target residual risk level"
        col_resid = "Residual risk level"
        col_resp = "Response"
        if col_target in df.columns:
            target = norm_str(row[col_target])
            if not target:
                add_failure(failures, "TARGET_RESIDUAL_NOT_BLANK", "BLOCKER", idx, row_key, col_target, target,
                            "Renseigner le Target residual risk level.")
            else:
                resp = norm_str(row.get(col_resp, ""))
                if resp == "Mitigate" and col_resid in df.columns:
                    resid = norm_str(row[col_resid])
                    target_num = first_digit_1_to_4(target)
                    resid_num = first_digit_1_to_4(resid)
                    if target_num is None or resid_num is None:
                        add_failure(
                            failures, "TARGET_RESIDUAL_PARSE_DIGIT", "MAJOR", idx, row_key, col_target, target,
                            "Pour Response='Mitigate', Target residual risk level et Residual risk level doivent contenir un chiffre 1 à 4 pour comparaison."
                        )
                    else:
                        if not (target_num < resid_num):
                            add_failure(
                                failures, "TARGET_RESIDUAL_STRICTLY_LOWER_WHEN_MITIGATE", "MAJOR", idx, row_key, col_target, target,
                                f"Pour Response='Mitigate', le Target residual risk level ({target_num}) doit être strictement inférieur au Residual risk level ({resid_num})."
                            )

        # 19) Next review date -> must be last day of month + format yyyy-MM-dd (we validate as date + last day)
        col = "Next review date"
        if col in df.columns:
            raw = row[col]
            dt = parse_date_any(raw)
            if dt is None:
                add_failure(failures, "NEXT_REVIEW_DATE_NOT_BLANK_OR_VALID", "MAJOR", idx, row_key, col, norm_str(raw),
                            "Renseigner Next review date au format 'yyyy-MM-dd' (date valide).")
            else:
                last_day = last_day_of_month(dt)
                if dt.day != last_day:
                    add_failure(
                        failures, "NEXT_REVIEW_DATE_LAST_DAY_OF_MONTH", "MAJOR", idx, row_key, col, dt.strftime("%Y-%m-%d"),
                        f"La Next review date doit être le dernier jour du mois. Exemple pour {dt.strftime('%Y-%m')}: {dt.year}-{dt.month:02d}-{last_day:02d}."
                    )

    failures_df = pd.DataFrame(failures)

    # Summary and stats
    total_rows = len(df)
    total_failures = len(failures_df)

    if total_rows == 0:
        conformity = 100.0
    else:
        # Not a perfect "compliance %" (needs denominator = nb rules * rows), but still useful
        conformity = None

    rule_stats = (
        failures_df.groupby(["rule_id", "severity"], dropna=False)
        .size()
        .reset_index(name="failures_count")
        .sort_values(["severity", "failures_count"], ascending=[True, False])
    ) if not failures_df.empty else pd.DataFrame(columns=["rule_id", "severity", "failures_count"])

    summary = pd.DataFrame([{
        "rows_analyzed": total_rows,
        "failures_total": total_failures,
        "distinct_rules_failed": failures_df["rule_id"].nunique() if not failures_df.empty else 0,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    return summary, failures_df, rule_stats


def generate_report(input_xlsx_path: str, output_xlsx_path: str, sheet_name=None):
    # Read excel
    df = pd.read_excel(input_xlsx_path, sheet_name=sheet_name)

    summary, failures_df, rule_stats = run_quality_checks(df)

    # Add some helpful ordering
    if not failures_df.empty:
        failures_df = failures_df.sort_values(["severity", "rule_id", "row_index"], ascending=[True, True, True])

    with pd.ExcelWriter(output_xlsx_path, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="Summary")
        rule_stats.to_excel(writer, index=False, sheet_name="Rule_stats")
        failures_df.to_excel(writer, index=False, sheet_name="Failures")

    print(f"✅ Report generated: {output_xlsx_path}")


if __name__ == "__main__":
    # === A MODIFIER ===
    INPUT_FILE = "risk_cards.xlsx"              # ton fichier ServiceNow
    OUTPUT_FILE = "risk_cards_quality_report.xlsx"

    # sheet_name=None -> première feuille; sinon mettre le nom exact
    generate_report(INPUT_FILE, OUTPUT_FILE, sheet_name=None)