import dataiku
import numpy as np
import pandas as pd
import umap
import hdbscan
from sklearn.preprocessing import normalize
from sklearn.metrics import silhouette_score

RANDOM_STATE = 42

# ============================================================
# 1. Lecture
# ============================================================
df_pca = dataiku.Dataset("pca").get_dataframe()
id_col, desc_col = "LB_REF", "LB_DESC"
pca_cols = [c for c in df_pca.columns if c.startswith("pca_")]
X_pca = normalize(df_pca[pca_cols].values)
print(f"Corpus : {X_pca.shape[0]} incidents, {X_pca.shape[1]} dims PCA")

# ============================================================
# 2. UMAP vers dimensions intermédiaires (PAS 2D)
#    -> renforce la structure de densité pour HDBSCAN
# ============================================================
UMAP_DIMS = [10, 15]
umap_spaces = {}

for d in UMAP_DIMS:
    print(f"\nUMAP -> {d}D en cours...")
    reducer = umap.UMAP(
        n_neighbors=15,
        min_dist=0.0,          # 0.0 : optimal AVANT clustering (compacte les groupes)
        n_components=d,
        metric="cosine",
        random_state=RANDOM_STATE,
    )
    umap_spaces[d] = reducer.fit_transform(X_pca)
    print(f"  shape : {umap_spaces[d].shape}")

# ============================================================
# 3. Balayage HDBSCAN sur chaque espace
# ============================================================
rows = []

def evaluate(space_name, X, min_cluster_size, min_samples):
    cl = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric="euclidean",
        cluster_selection_method="eom",   # 'eom' = clusters de tailles variées
        prediction_data=True,
    )
    lab = cl.fit_predict(X)
    n_clusters = len(set(lab)) - (1 if -1 in lab else 0)
    noise_pct = float((lab == -1).mean())

    mask = lab != -1
    sil = np.nan
    if n_clusters > 1 and mask.sum() > 100:
        sil = silhouette_score(X[mask], lab[mask])

    sizes = pd.Series(lab[mask]).value_counts() if mask.sum() else pd.Series(dtype=int)
    return {
        "space": space_name,
        "min_cluster_size": min_cluster_size,
        "min_samples": min_samples,
        "n_clusters": n_clusters,
        "noise_pct": round(noise_pct, 4),
        "silhouette_hors_bruit": round(float(sil), 4) if not np.isnan(sil) else None,
        "taille_min": int(sizes.min()) if len(sizes) else 0,
        "taille_max": int(sizes.max()) if len(sizes) else 0,
        "taille_mediane": int(sizes.median()) if len(sizes) else 0,
    }, lab

# Grille de paramètres
GRID = [
    (50, 10), (80, 10), (100, 15), (150, 15), (200, 20),
]

best_labels = {}

# --- Baseline : HDBSCAN directement sur la PCA (pour comparaison) ---
for mcs, ms in GRID:
    res, lab = evaluate("pca_100d", X_pca, mcs, ms)
    rows.append(res)
    best_labels[f"pca_100d_{mcs}_{ms}"] = lab
    print(res)

# --- Sur les espaces UMAP ---
for d in UMAP_DIMS:
    for mcs, ms in GRID:
        res, lab = evaluate(f"umap_{d}d", umap_spaces[d], mcs, ms)
        rows.append(res)
        best_labels[f"umap_{d}d_{mcs}_{ms}"] = lab
        print(res)

df_sweep = pd.DataFrame(rows)
dataiku.Dataset("hdbscan_sweep").write_with_schema(df_sweep)

print("\n=== TOP configurations (triées par silhouette) ===")
print(df_sweep.sort_values("silhouette_hors_bruit", ascending=False).head(10).to_string())