import dataiku
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

ID_COL, DESC_COL, EVENT_COL = "LB_REF", "LB_DESC", "CD_EVENT_TYPE"
CLEAN_COL = "incident_description_cleaned"   # lemmatized, codes stripped
EXAMPLE_MAX_CHARS, N_EXAMPLES = 1500, 5

final = dataiku.Dataset("incidents_clustered").get_dataframe()

# Bring in the cleaned text: raw text is right for embeddings,
# cleaned text is right for extracting readable cluster terms.
cleaned = (dataiku.Dataset("incidents_nlp_cleaned_final")
           .get_dataframe()[[ID_COL, CLEAN_COL]]
           .drop_duplicates(subset=[ID_COL]))
final = final.merge(cleaned, on=ID_COL, how="left")

work = final[final["cluster"] != -1].copy()

cv = CountVectorizer(min_df=5, max_df=0.60, ngram_range=(1, 2))
M = cv.fit_transform(work[CLEAN_COL].fillna("").astype(str))
vocab = np.array(cv.get_feature_names_out())
labels = work["cluster"].values
corpus_rate = (np.asarray(M.sum(axis=0)).ravel() + 1.0) / M.shape[0]

profiles = []
for c in sorted(set(labels)):
    mask = labels == c
    n = int(mask.sum())
    sub = work[mask]

    freq = np.asarray(M[mask].sum(axis=0)).ravel()
    score = (freq / n) / corpus_rate
    score[freq < 5] = 0
    top_terms = vocab[np.argsort(score)[::-1][:12]]

    n_unique = int(sub[DESC_COL].str.strip().str.lower().nunique())
    et = sub[EVENT_COL].value_counts()
    reps = sub.nlargest(N_EXAMPLES, "membership")

    row = {
        "cluster": int(c),
        "size": n,
        "share_pct": round(100 * n / len(final), 2),
        "top_terms": ", ".join(top_terms),
        "repetition_factor": round(n / max(n_unique, 1), 1),
        "mean_membership": round(float(sub["membership"].mean()), 3),
        # Flags the clusters worth tagging first
        "quality_flag": ("STRONG" if sub["membership"].mean() >= 0.75
                         else "MEDIUM" if sub["membership"].mean() >= 0.55
                         else "WEAK"),
        "dominant_event_type": et.index[0] if len(et) else None,
        "event_type_purity": round(float(et.iloc[0] / n), 2) if len(et) else None,
        "n_event_types": int(sub[EVENT_COL].nunique()),
        "taxonomy_relation": ("ALIGNED" if len(et) and et.iloc[0] / n >= 0.85
                              else "PARTIAL" if len(et) and et.iloc[0] / n >= 0.60
                              else "CROSS_CUTTING"),
        "analyst_label": "",
        "analyst_comment": "",
    }
    for i in range(N_EXAMPLES):
        row[f"example_{i+1}_ref"] = reps.iloc[i][ID_COL] if i < len(reps) else ""
        row[f"example_{i+1}"] = (str(reps.iloc[i][DESC_COL])[:EXAMPLE_MAX_CHARS]
                                 if i < len(reps) else "")
    profiles.append(row)

prof = pd.DataFrame(profiles).sort_values("size", ascending=False).reset_index(drop=True)
dataiku.Dataset("cluster_profiles").write_with_schema(prof)

print(prof["quality_flag"].value_counts().to_string())
print(prof["taxonomy_relation"].value_counts().to_string())