import dataiku
import numpy as np
import pandas as pd
import umap
import hdbscan
from sklearn.feature_extraction.text import CountVectorizer

# ============================================================
# CONFIGURATION
# Selected from the HDBSCAN sweep: umap_10d / mcs=40 / ms=10 / eom
#   -> ~59 clusters, 80.4% coverage, silhouette 0.634
# ============================================================
RANDOM_STATE = 42
UMAP_DIMS = 10
MIN_CLUSTER_SIZE = 40
MIN_SAMPLES = 10
SELECTION_METHOD = "eom"

ID_COL = "LB_REF"
DESC_COL = "LB_DESC"                              # English text, as encoded
EVENT_COL = "CD_EVENT_TYPE"

# Cleaned/lemmatized text — used ONLY to extract readable cluster terms.
CLEAN_COL = "incident_description_cleaned"

N_EXAMPLES = 5
EXAMPLE_MAX_CHARS = 1500

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
    prediction_data=True,
).fit(X_clust)

labels = clusterer.labels_
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
noise_rate = (labels == -1).mean()

print(f"  clusters : {n_clusters}")
print(f"  noise    : {noise_rate:.1%}")
print(f"  coverage : {1 - noise_rate:.1%}")

df_pca["cluster"] = labels
df_pca["membership"] = clusterer.probabilities_

# ============================================================
# 3. SOFT ASSIGNMENT FOR NOISE POINTS
#    Attaches unclustered incidents to their nearest cluster with a
#    confidence score. Gives two usable levels: hard core vs full coverage.
#    Skipped gracefully if memory-constrained.
# ============================================================
is_noise = df_pca["cluster"] == -1
try:
    print("Computing soft assignment for noise points ...")
    soft = hdbscan.all_points_membership_vectors(clusterer)
    df_pca["cluster_assigned"] = np.where(is_noise, soft.argmax(axis=1), df_pca["cluster"])
    df_pca["assignment_confidence"] = np.where(is_noise, soft.max(axis=1), 1.0)
except Exception as e:
    print(f"  skipped ({e})")
    df_pca["cluster_assigned"] = df_pca["cluster"]
    df_pca["assignment_confidence"] = np.where(is_noise, 0.0, 1.0)

df_pca["is_core"] = ~is_noise

# ============================================================
# 4. JOIN METADATA, 2D COORDINATES AND CLEANED TEXT
# ============================================================
meta = (
    dataiku.Dataset("incidents_cleaned_final")
    .get_dataframe()[[ID_COL, EVENT_COL, CLEAN_COL]]
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

missing_clean = final[CLEAN_COL].isna().sum()
if missing_clean:
    print(f"WARNING: {missing_clean} rows have no cleaned text "
          f"(cluster terms will be less accurate for those)")

dataiku.Dataset("incidents_clustered").write_with_schema(final)
print(f"Wrote incidents_clustered: {len(final)} rows")

# ============================================================
# 5. CLUSTER PROFILES
#    Built on core members only, so the characterisation is not
#    diluted by borderline points.
# ============================================================
work = final[final["cluster"] != -1].copy()

cv = CountVectorizer(min_df=5, max_df=0.60, ngram_range=(1, 2))
M = cv.fit_transform(work[CLEAN_COL].fillna("").astype(str))
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
    score[freq < 5] = 0
    top_terms = vocab[np.argsort(score)[::-1][:12]]

    # Repetition factor: 1.0 = every description differs (true semantic
    # grouping); 8.0 = ~8 incidents share each wording (templated volume)
    n_unique = int(sub[DESC_COL].str.strip().str.lower().nunique())

    # Event type distribution -> reveals cross-taxonomy patterns
    et = sub[EVENT_COL].value_counts()
    purity = float(et.iloc[0] / n) if len(et) else np.nan

    mean_mb = float(sub["membership"].mean())
    reps = sub.nlargest(N_EXAMPLES, "membership")

    row = {
        "cluster": int(c),
        "size": n,
        "share_pct": round(100 * n / len(final), 2),
        "top_terms": ", ".join(top_terms),
        "n_unique_descriptions": n_unique,
        "repetition_factor": round(n / max(n_unique, 1), 1),
        "mean_membership": round(mean_mb, 3),
        # Tagging priority: STRONG clusters are the most cohesive
        "quality_flag": ("STRONG" if mean_mb >= 0.75
                         else "MEDIUM" if mean_mb >= 0.55
                         else "WEAK"),
        "dominant_event_type": et.index[0] if len(et) else None,
        "event_type_purity": round(purity, 2) if not np.isnan(purity) else None,
        "n_event_types": int(sub[EVENT_COL].nunique()),
        # CROSS_CUTTING = pattern invisible to the Basel taxonomy
        "taxonomy_relation": ("ALIGNED" if purity >= 0.85
                              else "PARTIAL" if purity >= 0.60
                              else "CROSS_CUTTING"),
        "mean_desc_length": int(sub["desc_length"].mean()),
        "analyst_label": "",
        "analyst_comment": "",
    }

    # Keep incident refs so analysts can trace examples back to RISK360
    for i in range(N_EXAMPLES):
        if i < len(reps):
            row[f"example_{i+1}_ref"] = reps.iloc[i][ID_COL]
            row[f"example_{i+1}"] = str(reps.iloc[i][DESC_COL])[:EXAMPLE_MAX_CHARS]
        else:
            row[f"example_{i+1}_ref"] = ""
            row[f"example_{i+1}"] = ""

    profiles.append(row)

prof = pd.DataFrame(profiles).sort_values("size", ascending=False).reset_index(drop=True)
dataiku.Dataset("cluster_profiles").write_with_schema(prof)
print(f"Wrote cluster_profiles: {len(prof)} clusters")

# ============================================================
# 6. DIAGNOSTICS
# ============================================================
print("\n--- Cluster quality ---")
print(prof["quality_flag"].value_counts().to_string())

print("\n--- Relation to Basel taxonomy ---")
print(prof["taxonomy_relation"].value_counts().to_string())

# Does truncation hurt? If unclustered descriptions are much longer,
# the 384-token model limit is likely degrading those embeddings.
print("\n--- Description length: core vs noise ---")
print(final.groupby("is_core")["desc_length"].agg(["count", "mean", "median"]).to_string())

# Language check: any cluster dominated by non-English text points to
# a gap in the upstream translation step.
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = RANDOM_STATE

    def safe_detect(t):
        try:
            return detect(t) if len(str(t)) > 40 else "short"
        except Exception:
            return "error"

    sample = final.sample(min(3000, len(final)), random_state=RANDOM_STATE).copy()
    sample["lang"] = sample[DESC_COL].apply(safe_detect)
    non_en = sample[~sample["lang"].isin(["en", "short", "error"])]

    print(f"\n--- Language check (sample of {len(sample)}) ---")
    print(sample["lang"].value_counts().head(6).to_string())
    if len(non_en):
        print(f"Non-English: {len(non_en)} ({len(non_en)/len(sample):.1%})")
        print("Most affected clusters:")
        print(non_en.groupby("cluster").size().sort_values(ascending=False).head(5).to_string())
except ImportError:
    print("\n(langdetect not available, language check skipped)")

print("\n--- Top 20 clusters by size ---")
cols = ["cluster", "size", "share_pct", "repetition_factor", "quality_flag",
        "taxonomy_relation", "event_type_purity", "dominant_event_type", "top_terms"]
pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 80)
print(prof[cols].head(20).to_string(index=False))