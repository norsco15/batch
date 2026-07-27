import numpy as np
from sklearn.neighbors import NearestNeighbors

df_umap = dataiku.Dataset("umap").get_dataframe()
coords = df_umap[["umap_x", "umap_y"]].values

nn = NearestNeighbors(n_neighbors=10).fit(coords)
dist, _ = nn.kneighbors(coords)
tightness = dist[:, 1:].mean(axis=1)

tight_idx = np.argsort(tightness)[:30]
for i in tight_idx[:12]:
    print(f"\n--- {df_umap.iloc[i]['LB_REF']} ---")
    print(df_umap.iloc[i]["LB_DESC"][:300])