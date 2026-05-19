import dataiku
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from scipy import sparse
import json
import os

# ============================================================================
# Configuration — discussed above, change with reason
# ============================================================================
MIN_DF = 5              # drop terms in <5 documents
MAX_DF = 0.7            # drop terms in >70% of documents
NGRAM_RANGE = (1, 2)    # unigrams and bigrams
MAX_FEATURES = 10000    # safety cap on vocabulary size

# ============================================================================
# Read input
# ============================================================================
input_ds = dataiku.Dataset("incidents_nlp_cleaned_final")
df = input_ds.get_dataframe()

print(f"Input rows: {len(df)}")

# ============================================================================
# Filter to rows with non-empty cleaned text — excluded rows can't be vectorized
# We KEEP them in the index dataset so the mapping stays complete, but flag them
# ============================================================================
df["included_in_vectorization"] = (
    df["incident_description_cleaned"].fillna("").str.len() > 0
)

print(f"Rows included in vectorization: {df['included_in_vectorization'].sum()}")
print(f"Rows excluded (empty cleaned text): {(~df['included_in_vectorization']).sum()}")

# Subset to vectorizable rows
vectorizable = df[df["included_in_vectorization"]].copy().reset_index(drop=True)
vectorizable["row_index"] = vectorizable.index

corpus = vectorizable["incident_description_cleaned"].tolist()

# ============================================================================
# TF vectorization
# ============================================================================
print("\nBuilding TF matrix...")
tf_vectorizer = CountVectorizer(
    min_df=MIN_DF,
    max_df=MAX_DF,
    ngram_range=NGRAM_RANGE,
    max_features=MAX_FEATURES,
    lowercase=False,  # already lowercased in cleaning
    token_pattern=r"(?u)\b\w+\b",  # default-like, but explicit
)
tf_matrix = tf_vectorizer.fit_transform(corpus)
tf_vocabulary = tf_vectorizer.get_feature_names_out().tolist()

print(f"  TF matrix shape: {tf_matrix.shape}")
print(f"  TF matrix density: {tf_matrix.nnz / (tf_matrix.shape[0] * tf_matrix.shape[1]):.4%}")
print(f"  Vocabulary size: {len(tf_vocabulary)}")

# ============================================================================
# TF-IDF vectorization (same parameters for fair comparison)
# ============================================================================
print("\nBuilding TF-IDF matrix...")
tfidf_vectorizer = TfidfVectorizer(
    min_df=MIN_DF,
    max_df=MAX_DF,
    ngram_range=NGRAM_RANGE,
    max_features=MAX_FEATURES,
    lowercase=False,
    token_pattern=r"(?u)\b\w+\b",
    sublinear_tf=True,  # log(1 + tf) — common default that handles long docs better
)
tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
tfidf_vocabulary = tfidf_vectorizer.get_feature_names_out().tolist()

print(f"  TF-IDF matrix shape: {tfidf_matrix.shape}")
print(f"  TF-IDF matrix density: {tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1]):.4%}")
print(f"  Vocabulary size: {len(tfidf_vocabulary)}")

# ============================================================================
# Diagnostic: top terms by aggregate weight in each matrix
# ============================================================================
print("\nTop 30 terms by total TF weight:")
tf_term_totals = np.asarray(tf_matrix.sum(axis=0)).flatten()
top_tf_indices = np.argsort(tf_term_totals)[::-1][:30]
for idx in top_tf_indices:
    print(f"  {tf_vocabulary[idx]:30s} {int(tf_term_totals[idx])}")

print("\nTop 30 terms by total TF-IDF weight:")
tfidf_term_totals = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
top_tfidf_indices = np.argsort(tfidf_term_totals)[::-1][:30]
for idx in top_tfidf_indices:
    print(f"  {tfidf_vocabulary[idx]:30s} {tfidf_term_totals[idx]:.2f}")

# ============================================================================
# Save matrices and vocabularies to the managed folder
# ============================================================================
output_folder = dataiku.Folder("vectorization_artifacts")
folder_path = output_folder.get_path()

print(f"\nSaving artifacts to {folder_path}...")

# Save sparse matrices as .npz files (efficient, scipy-native format)
sparse.save_npz(os.path.join(folder_path, "tf_matrix.npz"), tf_matrix)
sparse.save_npz(os.path.join(folder_path, "tfidf_matrix.npz"), tfidf_matrix)

# Save vocabularies as JSON for human readability
with open(os.path.join(folder_path, "tf_vocabulary.json"), "w") as f:
    json.dump(tf_vocabulary, f, indent=2)
with open(os.path.join(folder_path, "tfidf_vocabulary.json"), "w") as f:
    json.dump(tfidf_vocabulary, f, indent=2)

# Save the configuration used (helpful when revisiting later)
config = {
    "min_df": MIN_DF,
    "max_df": MAX_DF,
    "ngram_range": list(NGRAM_RANGE),
    "max_features": MAX_FEATURES,
    "n_documents": tf_matrix.shape[0],
    "tf_vocab_size": len(tf_vocabulary),
    "tfidf_vocab_size": len(tfidf_vocabulary),
}
with open(os.path.join(folder_path, "vectorization_config.json"), "w") as f:
    json.dump(config, f, indent=2)

# ============================================================================
# Write the index dataset
# ============================================================================
# We want the index to cover ALL rows of the original input, so downstream
# recipes can join by incident_id even for rows that weren't vectorized
index_df = df[[
    "incident_id",
    "included_in_vectorization",
    "incident_description_cleaned",  # convenient to have nearby
    "cleaned_word_count",
    "lang_detected",  # for diagnostics later
]].copy()

# Add row_index only for vectorized rows (NaN for excluded)
row_index_map = dict(zip(vectorizable["incident_id"], vectorizable["row_index"]))
index_df["row_index"] = index_df["incident_id"].map(row_index_map)

output_ds = dataiku.Dataset("vectorization_index")
output_ds.write_with_schema(index_df)

print("\nDone. Vectorization complete.")