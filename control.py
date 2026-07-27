import dataiku, numpy as np, pandas as pd, umap, hdbscan
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import CountVectorizer

RS = 42
MCS, MS, METHOD = 50, 10, "eom"          # ← ajuste selon le micro-sweep
ID, DESC = "LB_REF", "LB_DESC"
EVENT_COL = "CD_EVENT_TYPE"

# ---------- 1. Espace UMAP 15D + HDBSCAN ----------
df_pca = dataiku.Dataset("pca").get_dataframe()
X = normalize(df_pca[[c for c in df_pca.columns if c.startswith("pca_")]].values)

X15 = umap.UMAP(n_neighbors=15, min_dist=0.0, n_components=15,
                metric="cosine", random_state=RS).fit_transform(X)

clusterer = hdbscan.HDBSCAN(min_cluster_size=MCS, min_samples=MS,
                            cluster_selection_method=METHOD,
                            prediction_data=True).fit(X15)

df_pca["cluster"] = clusterer.labels_
df_pca["membership"] = clusterer.probabilities_   # force d'appartenance 0-1

# ---------- 2. Jointure métadonnées + coordonnées 2D ----------
meta = (dataiku.Dataset("incidents_cleaned_final").get_dataframe()
        [[ID, EVENT_COL]].drop_duplicates(subset=[ID]))
umap2d = dataiku.Dataset("umap").get_dataframe()[[ID, "umap_x", "umap_y"]]

final = (df_pca[[ID, DESC, "cluster", "membership"]]
         .merge(meta, on=ID, how="left")
         .merge(umap2d, on=ID, how="left"))

dataiku.Dataset("incidents_clustered").write_with_schema(final)

# ---------- 3. Profils de clusters ----------
work = final[final["cluster"] != -1].copy()
texts = work[DESC].fillna("").astype(str)

cv = CountVectorizer(min_df=5, max_df=0.6, ngram_range=(1, 2),
                     stop_words="english")
M = cv.fit_transform(texts)
vocab = np.array(cv.get_feature_names_out())
labels = work["cluster"].values

corpus_rate = (np.asarray(M.sum(axis=0)).ravel() + 1.0) / M.shape[0]

profiles = []
for c in sorted(set(labels)):
    mask = labels == c
    n = int(mask.sum())

    # Termes distinctifs (c-TF-IDF simplifié)
    freq = np.asarray(M[mask].sum(axis=0)).ravel()
    score = (freq / n) / corpus_rate
    score[freq < 5] = 0
    top = vocab[np.argsort(score)[::-1][:12]]

    sub = work[mask]
    # Ratio d'unicité : distingue clusters "template" et "sémantiques"
    uniq = sub[DESC].str.strip().str.lower().nunique() / n

    # Incidents représentatifs = plus forte appartenance
    reps = sub.nlargest(3, "membership")[DESC].str.slice(0, 220).tolist()

    # Event type dominant
    et = sub[EVENT_COL].value_counts()
    profiles.append({
        "cluster": int(c),
        "taille": n,
        "part_corpus_pct": round(100 * n / len(final), 2),
        "termes_cles": ", ".join(top),
        "ratio_unicite": round(float(uniq), 3),
        "type_cluster": "TEMPLATE" if uniq < 0.25 else ("MIXTE" if uniq < 0.6 else "SEMANTIQUE"),
        "event_type_dominant": et.index[0] if len(et) else None,
        "purete_event_type": round(float(et.iloc[0] / n), 2) if len(et) else None,
        "exemple_1": reps[0] if len(reps) > 0 else "",
        "exemple_2": reps[1] if len(reps) > 1 else "",
        "exemple_3": reps[2] if len(reps) > 2 else "",
        "libelle_analyste": "",          # ← à remplir en session de tagging
    })

prof = pd.DataFrame(profiles).sort_values("taille", ascending=False)
dataiku.Dataset("cluster_profiles").write_with_schema(prof)

print(f"\nBruit : {(final['cluster'] == -1).mean():.1%}")
print(prof["type_cluster"].value_counts())
print(prof[["cluster", "taille", "type_cluster", "purete_event_type", "termes_cles"]].head(25).to_string())