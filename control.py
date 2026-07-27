import dataiku
import numpy as np
import pandas as pd
import umap
import hdbscan
from sklearn.feature_extraction.text import CountVectorizer

# ============================================================
# CONFIGURATION — selected from the HDBSCAN sweep
# umap_10d / mcs=40 / ms=10 / eom
#   -> ~59 clusters, 80.4% coverage, silhouette 0.634
# ============================================================
RANDOM_STATE = 42
UMAP_DIMS = 10
MIN_CLUSTER_SIZE = 40
MIN_SAMPLES = 10
SELECTION_METHOD = "eom"

ID_COL = "LB_REF"
DESC_COL = "LB_DESC"            # English text carried over from compute_embeddings
EVENT_COL = "CD_EVENT_TYPE"

# ============================================================
# 1. BUILD THE CLUSTERING SPACE
#    Same geometry as the 2D UMAP recipe (no re-normalization,
#    euclidean metric) so the 2D map faithfully represents it.
#    min_dist=0.0 compacts groups -> better for density clustering.
# ============================================================
df_pca = dataiku.Dataset("pca").get_dataframe()
pca_cols = [c for c in df_pca.columns if c.startswith("pca_")]
X = df_pca[pca_cols].values

print(f"Input: {X.shape[0]} incidents, {X.shape[1]} PCA dimensions")
print(f"Fitting UMAP -> {UMAP_DIMS}D ...")

X_clust = umap.UMAP(
    n_neighbors=15,
    min_dist=0.0,
    n_components=UMAP_DIMS,
    metric="euclidean",
    random_state=RANDOM_STATE,
).fit_transform(X)

# ============================================================
# 2. HDBSCAN CLUSTERING
# ============================================================
print("Running HDBSCAN ...")

clusterer = hdbscan.HDBSCAN(
    min_cluster_size=MIN_CLUSTER_SIZE,
    min_samples=MIN_SAMPLES,
    metric="euclidean",
    cluster_selection_method=SELECTION_METHOD,
    prediction_data=True,       # required for soft assignment below
).fit(X_clust)

labels = clusterer.labels_
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
noise_rate = (labels == -1).mean()

print(f"  clusters : {n_clusters}")
print(f"  noise    : {noise_rate:.1%}")
print(f"  coverage : {1 - noise_rate:.1%}")

df_pca["cluster"] = labels
df_pca["membership"] = clusterer.probabilities_    # 0-1 strength of belonging

# ============================================================
# 3. SOFT ASSIGNMENT FOR NOISE POINTS
#    Noise points are attached to their nearest cluster with a
#    confidence score. Gives two usable levels:
#      - "cluster"          : hard core (high confidence)
#      - "cluster_assigned" : full coverage (with confidence flag)
# ============================================================
print("Computing soft assignment for noise points ...")

soft = hdbscan.all_points_membership_vectors(clusterer)
nearest = soft.argmax(axis=1)
confidence = soft.max(axis=1)

is_noise = df_pca["cluster"] == -1
df_pca["cluster_assigned"] = np.where(is_noise, nearest, df_pca["cluster"])
df_pca["assignment_confidence"] = np.where(is_noise, confidence, 1.0)
df_pca["is_core"] = ~is_noise

# ============================================================
# 4. JOIN METADATA AND 2D COORDINATES
# ============================================================
meta = (
    dataiku.Dataset("incidents_cleaned_final")
    .get_dataframe()[[ID_COL, EVENT_COL]]
    .drop_duplicates(subset=[ID_COL])
)
umap2d = dataiku.Dataset("umap").get_dataframe()[[ID_COL, "umap_x", "umap_y"]]

final = (
    df_pca[[ID_COL, DESC_COL, "cluster", "membership",
            "cluster_assigned", "assignment_confidence", "is_core"]]
    .merge(meta, on=ID_COL, how="left")
    .merge(umap2d, on=ID_COL, how="left")
)

final["desc_length"] = final[DESC_COL].fillna("").str.len()

dataiku.Dataset("incidents_clustered").write_with_schema(final)
print(f"Wrote incidents_clustered: {len(final)} rows")

# ============================================================
# 5. CLUSTER PROFILES
#    Built on core members only (cluster != -1), so the
#    characterisation is not diluted by borderline points.
# ============================================================
work = final[final["cluster"] != -1].copy()
texts = work[DESC_COL].fillna("").astype(str)

# Term-document matrix used only for interpretation (not clustering)
cv = CountVectorizer(
    min_df=5,
    max_df=0.60,
    ngram_range=(1, 2),
    stop_words="english",
)
M = cv.fit_transform(texts)
vocab = np.array(cv.get_feature_names_out())
work_labels = work["cluster"].values

# Corpus-level rate per term, used as the baseline for distinctiveness
corpus_rate = (np.asarray(M.sum(axis=0)).ravel() + 1.0) / M.shape[0]

profiles = []
for c in sorted(set(work_labels)):
    mask = work_labels == c
    n = int(mask.sum())
    sub = work[mask]

    # Distinctive terms: in-cluster rate divided by corpus rate
    freq = np.asarray(M[mask].sum(axis=0)).ravel()
    score = (freq / n) / corpus_rate
    score[freq < 5] = 0                      # ignore very rare terms
    top_terms = vocab[np.argsort(score)[::-1][:12]]

    # Repetition factor: how many distinct wordings per incident.
    # 1.0 = all descriptions differ; 8.0 = ~8 incidents per wording.
    n_unique = int(sub[DESC_COL].str.strip().str.lower().nunique())

    # Event type distribution -> reveals cross-taxonomy patterns
    et = sub[EVENT_COL].value_counts()

    # Most representative incidents = highest membership probability
    reps = sub.nlargest(3, "membership")[DESC_COL].str.slice(0, 250).tolist()

    profiles.append({
        "cluster": int(c),
        "size": n,
        "share_pct": round(100 * n / len(final), 2),
        "top_terms": ", ".join(top_terms),
        "n_unique_descriptions": n_unique,
        "repetition_factor": round(n / max(n_unique, 1), 1),
        "mean_membership": round(float(sub["membership"].mean()), 3),
        "dominant_event_type": et.index[0] if len(et) else None,
        "event_type_purity": round(float(et.iloc[0] / n), 2) if len(et) else None,
        "n_event_types": int(sub[EVENT_COL].nunique()),
        "mean_desc_length": int(sub["desc_length"].mean()),
        "example_1": reps[0] if len(reps) > 0 else "",
        "example_2": reps[1] if len(reps) > 1 else "",
        "example_3": reps[2] if len(reps) > 2 else "",
        "analyst_label": "",                  # to be filled in tagging sessions
        "analyst_comment": "",
    })

prof = pd.DataFrame(profiles).sort_values("size", ascending=False).reset_index(drop=True)
dataiku.Dataset("cluster_profiles").write_with_schema(prof)

# ============================================================
# 6. SANITY CHECKS
# ============================================================
print("\n--- Coverage ---")
print(f"Core members : {final['is_core'].sum()} ({final['is_core'].mean():.1%})")
print(f"Noise        : {(~final['is_core']).sum()} ({(~final['is_core']).mean():.1%})")

# Does truncation hurt? If noise descriptions are much longer than
# core ones, the 384-token limit is likely degrading those embeddings.
print("\n--- Description length: core vs noise ---")
print(final.groupby("is_core")["desc_length"].agg(["count", "mean", "median"]))

print("\n--- Cross-taxonomy check ---")
print("Clusters with purity < 0.5 (patterns cutting across Basel event types):")
cross = prof[prof["event_type_purity"] < 0.5]
print(f"  {len(cross)} / {len(prof)} clusters")

print("\n--- Top 20 clusters by size ---")
cols = ["cluster", "size", "share_pct", "repetition_factor",
        "event_type_purity", "n_event_types", "top_terms"]
print(prof[cols].head(20).to_string(index=False))