import dataiku
import pandas as pd

# ============================================================================
# Read the three input datasets
# ============================================================================
main_df = dataiku.Dataset("incidents_text_normalized").get_dataframe()
fr_df = dataiku.Dataset("incidents_translated_fr").get_dataframe()
it_df = dataiku.Dataset("incidents_translated_it").get_dataframe()

print(f"Main dataset: {len(main_df)} rows")
print(f"FR translations: {len(fr_df)} rows")
print(f"IT translations: {len(it_df)} rows")

# ============================================================================
# Standardize incident_id as string in all datasets (avoid join surprises)
# ============================================================================
main_df["incident_id"] = main_df["incident_id"].astype(str).str.strip()
fr_df["incident_id"] = fr_df["incident_id"].astype(str).str.strip()
it_df["incident_id"] = it_df["incident_id"].astype(str).str.strip()

# ============================================================================
# RENAME the translated text column in each FR/IT dataset to a common name
# ⚠️ ADJUST 'translated_text' to whatever your column is actually called
# ============================================================================
TRANSLATED_COL_NAME_FR = "translated_text"  # ← change to actual column name
TRANSLATED_COL_NAME_IT = "translated_text"  # ← change to actual column name

fr_df = fr_df[["incident_id", TRANSLATED_COL_NAME_FR]].rename(
    columns={TRANSLATED_COL_NAME_FR: "translation_from_fr"}
)
it_df = it_df[["incident_id", TRANSLATED_COL_NAME_IT]].rename(
    columns={TRANSLATED_COL_NAME_IT: "translation_from_it"}
)

# ============================================================================
# Sanity checks before merge
# ============================================================================
assert fr_df["incident_id"].is_unique, "Duplicate IDs in FR translations"
assert it_df["incident_id"].is_unique, "Duplicate IDs in IT translations"

# Confirm FR translations match FR-detected rows in main
fr_ids_in_main = set(main_df[main_df["lang_detected"] == "fr"]["incident_id"])
fr_ids_translated = set(fr_df["incident_id"])
missing_fr = fr_ids_in_main - fr_ids_translated
extra_fr = fr_ids_translated - fr_ids_in_main
if missing_fr:
    print(f"⚠️ {len(missing_fr)} FR incidents have no translation (will be excluded)")
if extra_fr:
    print(f"⚠️ {len(extra_fr)} translations have no matching FR incident in main")

# Same for IT
it_ids_in_main = set(main_df[main_df["lang_detected"] == "it"]["incident_id"])
it_ids_translated = set(it_df["incident_id"])
missing_it = it_ids_in_main - it_ids_translated
extra_it = it_ids_translated - it_ids_in_main
if missing_it:
    print(f"⚠️ {len(missing_it)} IT incidents have no translation")
if extra_it:
    print(f"⚠️ {len(extra_it)} IT translations have no matching incident")

# ============================================================================
# Left-join the translations onto the main dataset
# Left join preserves all rows from main, fills NaN where no translation exists
# ============================================================================
merged = main_df.merge(fr_df, on="incident_id", how="left")
merged = merged.merge(it_df, on="incident_id", how="left")

# ============================================================================
# Build the unified English column with clear priority rules:
#   1. If language was already English → keep the HTML-cleaned original
#   2. If language was French → use the FR translation
#   3. If language was Italian → use the IT translation
#   4. Otherwise (negligible other languages, unknown) → empty, will be excluded
# ============================================================================
def pick_english_text(row):
    lang = row["lang_detected"]
    if lang == "en":
        return row["incident_description_no_html"]
    elif lang == "fr":
        translated = row.get("translation_from_fr")
        return translated if isinstance(translated, str) and translated.strip() else ""
    elif lang == "it":
        translated = row.get("translation_from_it")
        return translated if isinstance(translated, str) and translated.strip() else ""
    else:
        return ""  # Spanish, unknown, etc. — excluded as agreed

merged["incident_description_en"] = merged.apply(pick_english_text, axis=1)

# ============================================================================
# Tracking columns for transparency and downstream filtering
# ============================================================================
merged["was_translated"] = merged["lang_detected"].isin(["fr", "it"]) & (
    merged["incident_description_en"].str.len() > 0
)
merged["excluded_from_clustering"] = (
    (merged["incident_description_en"].str.len() == 0) |
    (~merged["lang_detected"].isin(["en", "fr", "it"]))
)

# Drop the intermediate translation columns — they served their purpose
merged = merged.drop(columns=["translation_from_fr", "translation_from_it"])

# ============================================================================
# Summary
# ============================================================================
print(f"\n{'='*50}")
print(f"Total rows: {len(merged)}")
print(f"English passthrough: {(merged['lang_detected'] == 'en').sum()}")
print(f"FR translated and used: {((merged['lang_detected'] == 'fr') & (merged['incident_description_en'].str.len() > 0)).sum()}")
print(f"IT translated and used: {((merged['lang_detected'] == 'it') & (merged['incident_description_en'].str.len() > 0)).sum()}")
print(f"Excluded from clustering: {merged['excluded_from_clustering'].sum()}")

# Critical integrity check
assert len(merged) == len(main_df), "Row count changed during merge — investigate"

# ============================================================================
# Write output
# ============================================================================
output_ds = dataiku.Dataset("incidents_translated")
output_ds.write_with_schema(merged)
print("\nDone.")