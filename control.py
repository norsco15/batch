import dataiku
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from scipy import sparse
import json
import os
import tempfile
import io

# ============================================================================
# Configuration
# ============================================================================
MIN_DF = 5
MAX_DF = 0.7
NGRAM_RANGE = (1, 2)
MAX_FEATURES = 10000

# ============================================================================
# Read input
# ============================================================================
input_ds = dataiku.Dataset("incidents_nlp_cleaned_final")
df = input_ds.get_dataframe()

print(f"Input rows: {len(df)}")

# ============================================================================
# Filter to rows with non-empty cleaned text
# ============================================================================
df["included_in_vectorization"] = (
    df["incident_description_cleaned"].fillna("").str.len() > 0
)

print(f"Rows included in vectorization: {df['included_in_vectorization'].sum()}")
print(f"Rows excluded (empty cleaned text): {(~df['included_in_vectorization']).sum()}")

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
    lowercase=False,
    token_pattern=r"(?u)\b\w+\b",
)
tf_matrix = tf_vectorizer.fit_transform(corpus)
tf_vocabulary = tf_vectorizer.get_feature_names_out().tolist()

print(f"  TF matrix shape: {tf_matrix.shape}")
print(f"  TF matrix density: {tf_matrix.nnz / (tf_matrix.shape[0] * tf_matrix.shape[1]):.4%}")
print(f"  Vocabulary size: {len(tf_vocabulary)}")

# ============================================================================
# TF-IDF vectorization
# ============================================================================
print("\nBuilding TF-IDF matrix...")
tfidf_vectorizer = TfidfVectorizer(
    min_df=MIN_DF,
    max_df=MAX_DF,
    ngram_range=NGRAM_RANGE,
    max_features=MAX_FEATURES,
    lowercase=False,
    token_pattern=r"(?u)\b\w+\b",
    sublinear_tf=True,
)
tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
tfidf_vocabulary = tfidf_vectorizer.get_feature_names_out().tolist()

print(f"  TF-IDF matrix shape: {tfidf_matrix.shape}")
print(f"  TF-IDF matrix density: {tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1]):.4%}")
print(f"  Vocabulary size: {len(tfidf_vocabulary)}")

# ============================================================================
# Diagnostic prints
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
# Save artifacts to the HDFS-backed managed folder
# ============================================================================
output_folder = dataiku.Folder("vectorization_artifacts")

print("\nSaving artifacts to managed folder (HDFS)...")


def upload_sparse_matrix(folder, file_name, matrix):
    """
    Save a scipy sparse matrix to an HDFS-backed managed folder.
    
    scipy.sparse.save_npz requires a local file path, so we write to a temp file
    first, then stream it into the managed folder.
    """
    with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        sparse.save_npz(tmp_path, matrix)
        with open(tmp_path, "rb") as f:
            folder.upload_stream(file_name, f)
        print(f"  Uploaded {file_name}")
    finally:
        # Clean up the local temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def upload_json(folder, file_name, obj):
    """Save a Python object as JSON in the managed folder."""
    data = json.dumps(obj, indent=2).encode("utf-8")
    folder.upload_data(file_name, data)
    print(f"  Uploaded {file_name}")


# Upload the sparse matrices
upload_sparse_matrix(output_folder, "tf_matrix.npz", tf_matrix)
upload_sparse_matrix(output_folder, "tfidf_matrix.npz", tfidf_matrix)

# Upload the vocabularies
upload_json(output_folder, "tf_vocabulary.json", tf_vocabulary)
upload_json(output_folder, "tfidf_vocabulary.json", tfidf_vocabulary)

# Upload the configuration
config = {
    "min_df": MIN_DF,
    "max_df": MAX_DF,
    "ngram_range": list(NGRAM_RANGE),
    "max_features": MAX_FEATURES,
    "n_documents": tf_matrix.shape[0],
    "tf_vocab_size": len(tf_vocabulary),
    "tfidf_vocab_size": len(tfidf_vocabulary),
}
upload_json(output_folder, "vectorization_config.json", config)

# ============================================================================
# Write the index dataset (this part is unchanged — datasets aren't HDFS-specific)
# ============================================================================
index_df = df[[
    "incident_id",
    "included_in_vectorization",
    "incident_description_cleaned",
    "cleaned_word_count",
    "lang_detected",
]].copy()

row_index_map = dict(zip(vectorizable["incident_id"], vectorizable["row_index"]))
index_df["row_index"] = index_df["incident_id"].map(row_index_map)

output_ds = dataiku.Dataset("vectorization_index")
output_ds.write_with_schema(index_df)

print("\nDone. Vectorization complete.")