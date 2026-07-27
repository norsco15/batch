import dataiku
import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (silhouette_score, davies_bouldin_score,
                             calinski_harabasz_score, adjusted_rand_score)

RANDOM_STATE = 42

# ---------- Lecture ----------
df = dataiku.Dataset("pca").get_dataframe()
id_col, desc_col = "LB_REF", "LB_DESC"
pca_cols = [c for c in df.columns if c.startswith("pca_")]
X = normalize(df[pca_cols].values)   # re-normalisation

# ---------- Stabilité : ARI moyen sur bootstraps ----------
def stability_score(X, k, n_runs=5, sample_frac=0.8, seed=RANDOM_STATE):
    """Clusterise des sous-échantillons, compare les labels sur l'intersection.
    ARI proche de 1 = partition stable, insensible à l'échantillon."""
    rng = np.random.RandomState(seed)
    n = X.shape[0]
    runs = []
    for r in range(n_runs):
        idx = rng.choice(n, int(sample_frac * n), replace=False)
        km = KMeans(n_clusters=k, n_init=10, random_state=seed + r).fit(X[idx])
        labels_full = km.predict(X)          # projette sur tout le corpus
        runs.append(labels_full)
    aris = [adjusted_rand_score(runs[i], runs[j])
            for i in range(len(runs)) for j in range(i + 1, len(runs))]
    return float(np.mean(aris))

# ---------- Balayage ----------
rows = []
for k in range(4, 21):
    km = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE)
    lab_km = km.fit_predict(X)

    gmm = GaussianMixture(n_components=k, covariance_type="diag",
                          random_state=RANDOM_STATE)
    lab_gmm = gmm.fit_predict(X)

    rows.append({
        "k": k,
        "sil_kmeans": silhouette_score(X, lab_km, sample_size=5000, random_state=RANDOM_STATE),
        "sil_gmm":    silhouette_score(X, lab_gmm, sample_size=5000, random_state=RANDOM_STATE),
        "davies_bouldin_kmeans": davies_bouldin_score(X, lab_km),   # plus bas = mieux
        "calinski_kmeans":       calinski_harabasz_score(X, lab_km), # plus haut = mieux
        "stability_ari":         stability_score(X, k),
        "min_cluster_size":      int(pd.Series(lab_km).value_counts().min()),
        "max_cluster_size":      int(pd.Series(lab_km).value_counts().max()),
        "inertia":               km.inertia_,   # pour la courbe du coude
    })
    print(rows[-1])

dataiku.Dataset("clustering_k_sweep").write_with_schema(pd.DataFrame(rows))



