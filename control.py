import re
import unicodedata
from datetime import datetime, date
import pandas as pd
from bs4 import BeautifulSoup


# -----------------------
# 1. Nettoyage Action Plan
# -----------------------

def clean_action_plan_description(file_path: str) -> str:
    df = pd.read_excel(file_path)

    def clean_html(html):
        if pd.isna(html):
            return ""
        soup = BeautifulSoup(str(html), "html.parser")
        return soup.get_text(separator="\n")

    df["Action Plan"] = df["Action Plan"].apply(clean_html)

    cleaned_file_path = "cleaned_" + file_path
    df.to_excel(cleaned_file_path, index=False)
    print(f"The cleanup process is completed, cleaned file saved as: {cleaned_file_path}")
    return cleaned_file_path


# -----------------------
# 2. Utilitaires dates / mois
# -----------------------

# Tous les alias de mois qu'on veut reconnaître (minuscule, sans accent)
MONTH_ALIASES = {
    # January
    "jan": 1, "janv": 1, "january": 1, "janvier": 1,
    # February
    "feb": 2, "february": 2, "fev": 2, "fevr": 2, "fevrier": 2,
    # March
    "mar": 3, "march": 3, "mars": 3,
    # April
    "apr": 4, "april": 4, "avr": 4, "avril": 4,
    # May
    "may": 5, "mai": 5,
    # June
    "jun": 6, "june": 6, "juin": 6,
    # July
    "jul": 7, "july": 7, "juil": 7, "juillet": 7,
    # August
    "aug": 8, "august": 8, "aout": 8, "août": 8,
    # September
    "sep": 9, "sept": 9, "september": 9, "septembre": 9,
    # October
    "oct": 10, "october": 10, "octobre": 10,
    # November
    "nov": 11, "november": 11, "novembre": 11,
    # December
    "dec": 12, "december": 12, "decembre": 12,
}

# Regex sur noms de mois (dans un texte déjà normalisé sans accents)
MONTH_NAME_PATTERN = re.compile(
    r"\b(" + "|".join(sorted(MONTH_ALIASES.keys(), key=len, reverse=True)) + r")\b\s*(\d{4})?",
    flags=re.IGNORECASE,
)

# Patterns numériques typiques
DATE_PATTERNS = [
    # 2025-10-15 ou 2025/10/15
    re.compile(r"\b(20\d{2})[-/](0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])\b"),
    # 15-10-2025 ou 15/10/2025
    re.compile(r"\b(0?[1-9]|[12]\d|3[01])[-/](0?[1-9]|1[0-2])[-/](20\d{2})\b"),
    # 20251015
    re.compile(r"\b(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\b"),
    # 10/2025 ou 10-2025
    re.compile(r"\b(0?[1-9]|1[0-2])[-/](20\d{2})\b"),
]


def _normalize_text(text: str) -> str:
    """Minuscule + suppression des accents."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _infer_year_for_month(month: int, reference_date: date) -> int:
    """
    Si le mois est donné sans année, on suppose qu'il s'agit de
    la dernière occurrence de ce mois AVANT la reference_date.
    """
    year = reference_date.year
    if month > reference_date.month:
        year -= 1
    return year


def extract_dates_from_text(text: str, reference_date: date) -> list[date]:
    """
    Retourne une liste de dates (au 1er du mois) détectées dans le texte :
    - noms de mois FR/EN (+/- année)
    - formats numériques (YYYY-MM-DD, DD/MM/YYYY, YYYYMMDD, MM/YYYY, …)
    """
    if not isinstance(text, str) or not text.strip():
        return []

    normalized = _normalize_text(text)
    dates: list[date] = []

    # 1) Noms de mois FR/EN
    for m in MONTH_NAME_PATTERN.finditer(normalized):
        month_key = m.group(1)
        year_str = m.group(2)
        month = MONTH_ALIASES.get(month_key.lower())
        if not month:
            continue
        if year_str:
            year = int(year_str)
        else:
            year = _infer_year_for_month(month, reference_date)
        dates.append(date(year, month, 1))

    # 2) Formats numériques
    for pattern in DATE_PATTERNS:
        for m in pattern.finditer(text):
            g = m.groups()
            # On harmonise en (year, month, day)
            if pattern is DATE_PATTERNS[0]:       # YYYY-MM-DD
                year, month, day = int(g[0]), int(g[1]), int(g[2])
            elif pattern is DATE_PATTERNS[1]:     # DD-MM-YYYY
                day, month, year = int(g[0]), int(g[1]), int(g[2])
            elif pattern is DATE_PATTERNS[2]:     # YYYYMMDD
                year, month, day = int(g[0]), int(g[1]), int(g[2])
            else:                                 # MM-YYYY
                month, year = int(g[0]), int(g[1])
                day = 1

            try:
                d = date(year, month, day)
            except ValueError:
                continue
            # On ne garde que le mois (1er du mois)
            dates.append(date(d.year, d.month, 1))

    # On supprime les doublons
    dates = sorted(set(dates))
    return dates


def month_diff(d1: date, d2: date) -> int:
    """Nombre de mois entiers entre d1 et d2 (d1 >= d2 ou pas, on prend la valeur absolue)."""
    return abs((d1.year - d2.year) * 12 + (d1.month - d2.month))


# -----------------------
# 3. Contrôle "Monthly Comment"
# -----------------------

def extract_monthly_comment_block(action_plan_text: str) -> str:
    """
    Récupère uniquement la partie à partir de 'Monthly Comment :' (si présent),
    sinon on renvoie tout le texte.
    """
    if not isinstance(action_plan_text, str):
        return ""
    m = re.search(r"monthly\s*comment\s*:(.*)", action_plan_text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1)
    return action_plan_text


def check_monthly_comment_quality(text: str, planned_end_date) -> tuple[bool, str, str | None]:
    """
    Retourne :
    - ok (True/False)
    - raison (str)
    - dernière date détectée au format YYYY-MM (ou None)

    Règle proposée :
    - si aucune date / mois détecté  -> False
    - sinon, on regarde la dernière date <= ref_date
      où ref_date = min(today, planned_end_date ou today)
    - le commentaire est OK si cette date a <= 2 mois de retard
      par rapport à ref_date (paramétrable).
    """
    MAX_GAP_MONTHS = 2  # à ajuster selon ta tolérance

    today = datetime.today().date()
    if pd.notna(planned_end_date):
        try:
            ped = pd.to_datetime(planned_end_date).date()
        except Exception:
            ped = today
    else:
        ped = today

    # On ne veut pas exiger de commentaires dans le futur -> ref = min(today, ped)
    ref_date = min(today, ped)

    comment_block = extract_monthly_comment_block(text)
    dates = extract_dates_from_text(comment_block, ref_date)

    if not dates:
        return False, "Aucun mois / date détecté dans Monthly Comment", None

    # On prend la dernière date <= ref_date si possible, sinon la dernière tout court
    past_or_equal = [d for d in dates if d <= ref_date]
    if past_or_equal:
        last_date = max(past_or_equal)
    else:
        last_date = max(dates)

    gap = month_diff(ref_date, last_date)

    if gap <= MAX_GAP_MONTHS:
        return True, f"OK (dernier commentaire {last_date.strftime('%Y-%m')}, écart {gap} mois)", last_date.strftime("%Y-%m")
    else:
        return False, f"Dernier commentaire trop ancien ({last_date.strftime('%Y-%m')}, écart {gap} mois)", last_date.strftime("%Y-%m")


def check_monthly_comments(file_path: str) -> str:
    df = pd.read_excel(file_path)

    results = df.apply(
        lambda row: check_monthly_comment_quality(
            row.get("Action Plan", ""),
            row.get("Planned end date", None),
        ),
        axis=1,
        result_type="expand",
    )
    # results contient 3 colonnes (ok, reason, last_month)
    df["Monthly Comment OK"] = results[0]
    df["Monthly Comment reason"] = results[1]
    df["Monthly Comment last month"] = results[2]

    result_file_path = "monthly_comments_check_" + file_path
    df.to_excel(result_file_path, index=False)
    print(f"Monthly comments check saved as {result_file_path}")
    return result_file_path
