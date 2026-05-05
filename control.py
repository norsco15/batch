import dataiku
import pandas as pd
from transformers import MarianMTModel, MarianTokenizer
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# One translation model per source language → English
MODELS = {
    "fr": "Helsinki-NLP/opus-mt-fr-en",
    "it": "Helsinki-NLP/opus-mt-it-en",
    "es": "Helsinki-NLP/opus-mt-es-en",
}

# Load all models upfront (downloaded on first use, cached locally afterward)
tokenizers = {}
models = {}
for lang, model_name in MODELS.items():
    print(f"Loading {model_name}...")
    tokenizers[lang] = MarianTokenizer.from_pretrained(model_name)
    models[lang] = MarianMTModel.from_pretrained(model_name).to(device)


def translate_batch(texts, source_lang):
    """Translate a list of texts from source_lang to English."""
    if source_lang not in tokenizers:
        return [""] * len(texts)
    
    tokenizer = tokenizers[source_lang]
    model = models[source_lang]
    
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=512)
    
    return [tokenizer.decode(t, skip_special_tokens=True) for t in outputs]


# Read input
input_ds = dataiku.Dataset("incidents_text_normalized")
df = input_ds.get_dataframe()

# Load translation cache from previous run (if any)
try:
    cache_ds = dataiku.Dataset("incidents_translated")
    cache_df = cache_ds.get_dataframe()
    cached = dict(zip(cache_df["incident_id"], cache_df["incident_description_en"]))
    print(f"Loaded {len(cached)} cached translations")
except Exception:
    cached = {}
    print("No cache available — translating from scratch")


# Initialize the output column
df["incident_description_en"] = ""

# English passthrough (no translation needed)
en_mask = df["lang_detected"] == "en"
df.loc[en_mask, "incident_description_en"] = df.loc[en_mask, "incident_description_no_html"]
print(f"English passthrough: {en_mask.sum()} rows")

# Cached translations
cached_mask = df["incident_id"].isin(cached.keys()) & ~en_mask
n_cached_used = 0
for idx in df[cached_mask].index:
    cached_value = cached.get(df.at[idx, "incident_id"], "")
    if isinstance(cached_value, str) and cached_value.strip() != "":
        df.at[idx, "incident_description_en"] = cached_value
        n_cached_used += 1
print(f"Used cache for: {n_cached_used} rows")

# Translate remaining rows, batched by language for GPU efficiency
to_translate_mask = (
    ~en_mask 
    & ~cached_mask 
    & df["lang_detected"].isin(MODELS.keys())
    & (df["incident_description_no_html"].str.len() > 0)
)

BATCH_SIZE = 16  # decrease if you hit memory issues; increase if you have GPU room

for lang in MODELS.keys():
    lang_mask = to_translate_mask & (df["lang_detected"] == lang)
    indices = df[lang_mask].index.tolist()
    if not indices:
        continue
    
    print(f"Translating {len(indices)} {lang} texts...")
    
    for i in range(0, len(indices), BATCH_SIZE):
        batch_idx = indices[i:i+BATCH_SIZE]
        batch_texts = df.loc[batch_idx, "incident_description_no_html"].tolist()
        try:
            translations = translate_batch(batch_texts, lang)
            for j, idx in enumerate(batch_idx):
                df.at[idx, "incident_description_en"] = translations[j]
        except Exception as e:
            print(f"  Batch failed at index {i}: {e}")
            # Leave these rows with empty translations — they'll be excluded later
            continue
        
        if (i // BATCH_SIZE) % 10 == 0:
            print(f"  Progress: {min(i + BATCH_SIZE, len(indices))}/{len(indices)}")

# Tracking columns
df["was_translated"] = (df["lang_detected"] != "en") & (df["incident_description_en"].str.len() > 0)
df["translation_failed"] = (
    df["lang_detected"].isin(MODELS.keys()) 
    & (df["incident_description_en"].str.len() == 0)
)
df["excluded_from_clustering"] = df["incident_description_en"].str.len() == 0

print(f"\nFinal counts:")
print(f"  Translated: {df['was_translated'].sum()}")
print(f"  Translation failed: {df['translation_failed'].sum()}")
print(f"  Excluded from clustering: {df['excluded_from_clustering'].sum()}")

output_ds = dataiku.Dataset("incidents_translated")
output_ds.write_with_schema(df)