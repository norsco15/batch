import dataiku
import pandas as pd
import re
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
import html

DetectorFactory.seed = 42  # makes langdetect deterministic across runs

MIN_TEXT_LENGTH_FOR_DETECTION = 20  # below this, language detection is unreliable

input_ds = dataiku.Dataset("incidents_final")
df = input_ds.get_dataframe()


def strip_html(text):
    """Remove HTML tags and decode entities. Robust to malformed HTML."""
    if not isinstance(text, str) or text == "":
        return ""
    
    # Decode entities first (handles &amp;, &nbsp;, &#8217; etc.)
    decoded = html.unescape(text)
    
    # Parse HTML — lxml is more tolerant of malformed input than html.parser
    try:
        soup = BeautifulSoup(decoded, "lxml")
    except Exception:
        soup = BeautifulSoup(decoded, "html.parser")
    
    # separator=' ' prevents '<p>foo</p><p>bar</p>' from becoming 'foobar'
    text_only = soup.get_text(separator=" ", strip=True)
    
    # Decode again in case BeautifulSoup left some entities
    text_only = html.unescape(text_only)
    
    # Clean special whitespace characters
    text_only = text_only.replace("\xa0", " ")    # non-breaking space
    text_only = text_only.replace("\u200b", "")   # zero-width space
    text_only = text_only.replace("\ufeff", "")   # byte-order mark
    
    # Collapse all whitespace
    text_only = re.sub(r"\s+", " ", text_only).strip()
    
    return text_only


def detect_language_safe(text):
    """Detect language with graceful failure on edge cases."""
    if not isinstance(text, str) or len(text.strip()) < MIN_TEXT_LENGTH_FOR_DETECTION:
        return "unknown"
    try:
        return detect(text)
    except Exception:
        return "unknown"


# Strip HTML
df["incident_description_no_html"] = df["incident_description"].apply(strip_html)

# Diagnostic: how many characters did HTML stripping remove?
df["html_stripped_char_diff"] = (
    df["incident_description"].fillna("").str.len()
    - df["incident_description_no_html"].str.len()
)

# Detect language on cleaned text
df["lang_detected"] = df["incident_description_no_html"].apply(detect_language_safe)

# Print summary so you can see what happened
print("Language distribution:")
print(df["lang_detected"].value_counts())
print(f"\nHTML chars removed: total {df['html_stripped_char_diff'].sum():,}, max in single row {df['html_stripped_char_diff'].max()}")

output_ds = dataiku.Dataset("incidents_text_normalized")
output_ds.write_with_schema(df)



# step 2
