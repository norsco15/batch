import dataiku
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 42  # reproducibility

ds = dataiku.Dataset("incidents_final")
df = ds.get_dataframe()

def safe_detect(text):
    try:
        if not isinstance(text, str) or len(text.strip()) < 20:
            return "unknown"
        return detect(text)
    except Exception:
        return "unknown"

df["lang_detected"] = df["incident_description"].apply(safe_detect)
print(df["lang_detected"].value_counts())