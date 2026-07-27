import dataiku
import numpy as np
import pandas as pd
import umap
import hdbscan
from sklearn.metrics import silhouette_score

RANDOM_STATE = 42

# ============================================================
# 1. Load PCA output (no re-normalization: already done upstream)
# ============================================================
df_pca = dataiku.Dataset("pca").get_dataframe()
id_col, desc_col = "LB_REF", "LB_DESC"
pca_cols = [c for c in df_pca.columns if c.startswith("pca_")]
X = df_pca[pca_cols].values
print(f"Corpus: {X.shape[0]} incidents, {X.shape[1]} PCA dims")

# ============================================================
# 2. Fit UMAP once per target dimension (the expensive part)
#    min_dist=0.0 -> compacts groups, optimal BEFORE clustering
#    metric="euclidean" -> aligned with the 2D visualization recipe
# ============================================================
UMAP_DIMS = [10, 15]
spaces = {}

for d in UMAP_DIMS:
    print(f"\nFitting UMAP -> {d}D ...")
    spaces[d] = umap.UMAP(
        n_neighbors=15,
        min_dist=0.0,
        n_components=d,
        metric="euclidean",
        random_state=RANDOM_STATE,
    ).fit_transform(X)
    print(f"  done, shape={spaces[d].shape}")

# ============================================================
# 3. Sweep HDBSCAN (cheap: reuses the fitted UMAP spaces)
# ============================================================
N_TOTAL = X.shape[0]
rows = []

for d, Xd in spaces.items():
    for mcs in [40, 50, 60, 80, 100]:
        for ms in [5, 10, 15]:
            for method in ["eom", "leaf"]:
                labels = hdbscan.HDBSCAN(
                    min_cluster_size=mcs,
                    min_samples=ms,
                    metric="euclidean",
                    cluster_selection_method=method,
                ).fit_predict(Xd)

                mask = labels != -1
                sizes = pd.Series(labels[mask]).value_counts()
                k = len(sizes)
                sil = np.nan
                if k > 1 and mask.sum() > 100:
                    sil = silhouette_score(Xd[mask], labels[mask])

                rows.append({
                    "space": f"umap_{d}d",
                    "min_cluster_size": mcs,
                    "min_samples": ms,
                    "method": method,
                    "n_clusters": k,
                    "noise_pct": round(float(1 - mask.mean()), 4),
                    "coverage_pct": round(float(mask.mean()), 4),
                    "silhouette": round(float(sil), 4) if not np.isnan(sil) else None,
                    "size_min": int(sizes.min()) if k else 0,
                    "size_max": int(sizes.max()) if k else 0,
                    "size_median": int(sizes.median()) if k else 0,
                    "max_share_pct": round(100 * float(sizes.max()) / N_TOTAL, 2) if k else 0,
                })

df_sweep = pd.DataFrame(rows)
dataiku.Dataset("hdbscan_sweep").write_with_schema(df_sweep)

# ============================================================
# 4. Shortlist: usable configs only
# ============================================================
shortlist = df_sweep[
    (df_sweep["n_clusters"].between(10, 50))
    & (df_sweep["max_share_pct"] < 12)
    & (df_sweep["noise_pct"] < 0.45)
    & (df_sweep["size_min"] >= 30)
].sort_values(["coverage_pct", "silhouette"], ascending=False)

print("\n=== SHORTLIST (usable configs, best coverage first) ===")
print(shortlist.head(15).to_string(index=False))