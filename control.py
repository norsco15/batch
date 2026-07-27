import umap, hdbscan, numpy as np, pandas as pd, dataiku
from sklearn.preprocessing import normalize
from sklearn.metrics import silhouette_score

df_pca = dataiku.Dataset("pca").get_dataframe()
X = normalize(df_pca[[c for c in df_pca.columns if c.startswith("pca_")]].values)

X15 = umap.UMAP(n_neighbors=15, min_dist=0.0, n_components=15,
                metric="cosine", random_state=42).fit_transform(X)

for mcs in [40, 50, 60, 70]:
    for method in ["eom", "leaf"]:
        lab = hdbscan.HDBSCAN(min_cluster_size=mcs, min_samples=10,
                              cluster_selection_method=method).fit_predict(X15)
        m = lab != -1
        s = pd.Series(lab[m]).value_counts()
        print(f"mcs={mcs} {method:4s} | k={len(s):3d} | bruit={1-m.mean():.1%} "
              f"| sil={silhouette_score(X15[m], lab[m]):.3f} | max={s.max():5d} | med={int(s.median())}")