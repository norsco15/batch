import dataiku
import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS as SPACY_STOPWORDS

# Load English spaCy model (already installed earlier).
# Parser enabled because for your long texts, sentence-aware tokenization
# produces better lemmas than parser-disabled mode.
nlp = spacy.load("en_core_web_sm", disable=["ner"])

input_ds = dataiku.Dataset("incidents_nlp_cleaned_regex")
df = input_ds.get_dataframe()

# Custom stop-words: start empty. After the first run, look at top-50 token
# frequencies and add any high-frequency non-discriminative words.
# Don't pre-remove OpRisk vocabulary like "client", "loss", "incident" —
# they may genuinely define clusters.
custom_stopwords = set()
stopwords = SPACY_STOPWORDS | custom_stopwords

MIN_TOKEN_LEN = 3


def clean_long_text(text_series, batch_size=100):
    """Lemmatize + remove stop-words on long English texts using spaCy."""
    texts = text_series.fillna("").astype(str).tolist()
    cleaned = []
    for doc in nlp.pipe(texts, batch_size=batch_size):
        tokens = []
        for t in doc:
            if t.is_stop or t.is_punct or t.is_space:
                continue
            lemma = t.lemma_.lower().strip()
            if not lemma or lemma in stopwords:
                continue
            if len(lemma) < MIN_TOKEN_LEN:
                continue
            if lemma.isdigit():
                continue
            tokens.append(lemma)
        cleaned.append(" ".join(tokens))
    return cleaned


# Apply to the English text column
df["incident_description_cleaned"] = clean_long_text(df["incident_description_en"])

# Diagnostics
df["cleaned_char_len"] = df["incident_description_cleaned"].str.len()
df["cleaned_word_count"] = df["incident_description_cleaned"].str.split().str.len().fillna(0).astype(int)
df["cleaned_is_empty"] = df["cleaned_char_len"] == 0

# Token reduction ratio — sanity-check the cleaning isn't too aggressive
df["token_reduction_ratio"] = (
    df["cleaned_word_count"] / df["regex_cleaned_word_count"].replace(0, 1)
)

# Summary
print(f"Total rows: {len(df)}")
print(f"Empty after cleaning: {df['cleaned_is_empty'].sum()}")
print(f"Median cleaned word count: {df['cleaned_word_count'].median()}")
print(f"Mean token reduction ratio: {df['token_reduction_ratio'].mean():.2f}")

output_ds = dataiku.Dataset("incidents_nlp_cleaned_final")
output_ds.write_with_schema(df)