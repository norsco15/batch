# MLION — Flow documentation

**MLION — Machine Learning Incident-Ops Navigator**
Owner: Zakaria GUAAYBESS (RISK) · Last updated: 9 October 2026

This page documents the Dataiku flow of MLION, from the raw incident descriptions to the clustering into root-cause families. It explains what each recipe does, why it is configured the way it is, and what each output contains.

Values marked **[TBC]** still need to be confirmed against the latest run. They are listed again at the end of the page.

---

## Contents

1. Purpose of the project
2. Flow overview
3. Data foundation
4. Text preparation: cleaning and language detection
5. Translation
6. Text cleaning for interpretation (TF / TF-IDF)
7. Embedding
8. PCA
9. UMAP 2D (visualisation)
10. UMAP 10D (clustering space)
11. Clustering
12. Output datasets: column dictionary
13. Known limitations
14. How to re-run the flow
15. Decision log
16. Values to confirm

---

## 1. Purpose of the project

Every operational risk incident in RISK360 carries a free-text description of what happened. These descriptions are stored but not analysed at scale, and the Basel event-type taxonomy alone cannot show which root causes keep recurring.

MLION uses NLP to group incidents that describe the same problem, even when they are worded differently, into **root-cause families**. The methodology is adapted from Di Vincenzo et al. (2023), *A text analysis for Operational Risk loss descriptions*, with two deliberate departures, both explained below:

- sentence embeddings (`all-mpnet-base-v2`) instead of word2vec on a bag-of-words matrix;
- density-based clustering (HDBSCAN) instead of k-means.

---

## 2. Flow overview

```
RISK360 extracts (Incidents, Causes, Consequences)
        │  aggregation 1-to-N, one row per incident
        ▼
Text preparation ── HTML stripping, language detection
        │
        ▼
Translation ─────── French / Italian → English (CIB AI Platform)
        │
        ├──────────────────────────────┐
        ▼                              ▼
Embedding                      Heavy cleaning (lemmatisation, stop words)
all-mpnet-base-v2, 768 dims    used ONLY to extract readable cluster terms
        │
        ▼
PCA ─────────── 768 → 120 dims, L2-normalised
        │
        ├────────────────────────┐
        ▼                        ▼
UMAP 2D                    UMAP 10D
map for the human eye      space used by the clustering
                                 │
                                 ▼
                     HDBSCAN sweep (calibration on a sample)
                                 │
                                 ▼
                     Final clustering + cluster profiles
```

**Main recipes and datasets (full-history corpus):**

| Step | Recipe | Output dataset |
|---|---|---|
| Embedding | `compute_HI_ALL_EMBEDDINGS` [TBC] | `HI_ALL_EMBEDDINGS` |
| PCA | `compute_HI_ALL_PCA` | `HI_ALL_PCA` |
| UMAP 2D | `compute_HI_ALL_UMAP` [TBC] | `HI_ALL_UMAP` |
| UMAP 10D | `compute_HI_ALL_UMAP_10D` | `HI_ALL_UMAP_10D` |
| Parameter sweep | `compute_HI_ALL_HDBSCAN_SWEEP` | `HI_ALL_HDBSCAN_SWEEP` |
| Clustering | `compute_HI_ALL_CLUSTERING` | `HI_ALL_INCIDENTS_CLUSTERED`, `HI_ALL_CLUSTER_PROFILES` |

The key that links every dataset is the incident reference **`LB_REF`**. Every recipe carries it through, so rows never depend on their order.

---

## 3. Data foundation

**Source:** three RISK360 datasets.

| Dataset | Content |
|---|---|
| Historical Incidents | the event itself: when, where, total loss, description |
| Causes | the underlying triggers (one incident → one or more causes) |
| Consequences | financial and non-financial impacts (one incident → one or more consequences) |

**The 1-to-N problem.** Joining the three datasets directly would duplicate an incident once per cause × consequence, inflating counts and loss amounts. On the 2025 validated incidents (10,105 incidents), 89% had one cause and 73% had one consequence, so duplication would have affected a large share of rows.

**Resolution.** Causes and consequences are aggregated per incident before the join, with field-specific logic (for example, consequence loss amounts are summed). As a consistency check, the summed loss matches the total loss field of the Historical Incidents dataset. Result: **one row per incident**.

**Scope.**

| Corpus | Incidents |
|---|---|
| 2025 validated incidents (first iteration) | 10,039 after exclusions |
| Full history since 1999 | 357,552 |
| Full history, excluding status *Closed* | ~315,000 [TBC exact count] |

The exclusion of *Closed* incidents is applied just before clustering, see section 11.6.

---

## 4. Text preparation: cleaning and language detection

**Recipe type:** Python.

1. **HTML stripping** with BeautifulSoup (`lxml` parser). Quoted text written as `<<...>>` is neutralised first, because the parser otherwise reads it as an HTML tag and deletes it.
2. **Language detection** with `langdetect`, seed fixed to 42 for reproducibility.

Language distribution on the 2025 corpus: 49% English, 43% French, 7% Italian, under 1% other. [TBC distribution on the full corpus.]

**Packages:** `beautifulsoup4`, `lxml`, `langdetect` (internal PyPI mirror).

---

## 5. Translation

The embedding model is English-only, so all descriptions must be in English before encoding. The native Dataiku translation plugin is not available in the environment, and external translation APIs are excluded for data-governance reasons.

**Workaround:**

1. French and Italian descriptions are extracted from the flow.
2. They are translated with the **CIB AI Platform** Translate tool (internal to the bank, so data never leaves the controlled environment).
3. The translations are re-imported and joined back to the master dataset on the incident ID.

On the 2025 corpus: 4,379 French + 684 Italian = 5,063 descriptions, translated in under four hours.

**Output column:** `LB_DESC_EN` — the English description, HTML removed, **not** lemmatised. This is the column fed to the embedding model.

> **Important.** An early run encoded the pre-translation column by mistake. The model then grouped incidents by language rather than by meaning: the 2D map showed two masses matching the English / French split. The embedding recipe now asserts that the input is English before encoding (section 7).

**Known residue:** on the 2025 corpus, one cluster of 292 incidents (~3%) was Italian text that had escaped translation. [TBC whether residues exist on the full corpus.]

---

## 6. Text cleaning for interpretation (TF / TF-IDF)

This branch does **not** feed the clustering. Embeddings are computed on natural English text (section 7). The heavily cleaned text is used only to extract readable, distinctive terms for each cluster.

**Steps (Prepare recipe, then Python):**

1. Lowercase; accent normalisation.
2. Punctuation removal.
3. Removal of tokens containing digits (regex `\b\w*[0-9]+\w*\b`) — removes references, dates and amounts such as `10k`, `11th`, `pr0258`.
4. Removal of standalone digits.
5. spaCy `en_core_web_sm`: lemmatisation, stop-word removal, minimum token length 3.

**Output column:** `incident_description_cleaned`.

**Vectorisation (2025 corpus, kept for reference):** TF and TF-IDF matrices with `min_df=10`, `max_df=0.7`, `ngram_range=(1, 2)`, `sublinear_tf=True` for TF-IDF; vocabulary of ~10,110 terms. Stored as sparse `.npz` files in the HDFS managed folder `vectorization_artifacts`.

---

## 7. Embedding

**Model:** `sentence-transformers/all-mpnet-base-v2`, installed in the Dataiku Python code environment by ITG from the GitHub mirror `homer6/all-mpnet-base-v2`. This is a tactical solution; the long-term target is official access through ModelHub.

**What it does.** Each description becomes a vector of **768 numbers** that represents its meaning. Two incidents describing the same problem in different words get close vectors.

**Why this model.** The corpus is in English at this stage (after translation), and `all-mpnet-base-v2` is the highest-quality general English sentence-embedding model of the sentence-transformers family. Sentence embeddings capture the meaning of a whole description, which suits our long texts better than the word-level word2vec used in the reference paper.

**Configuration:**

| Setting | Value | Why |
|---|---|---|
| Input column | `LB_DESC_EN` | natural English text; lemmatised text degrades sentence embeddings |
| Batch size | encoding in batches [TBC size] | encoding everything at once saturates memory |
| Language check | assertion: > 90% English on a sample | fails the recipe if the wrong column is encoded |

**Output:** `HI_ALL_EMBEDDINGS` — `LB_REF`, `LB_DESC_EN`, `emb_0` … `emb_767`.

**Limitation — truncation.** The model reads about 384 tokens (≈ 1,500 characters). On the 2025 corpus, 15.8% of descriptions were longer and 2.8% exceeded 3,000 characters; for those, only the beginning is encoded. Incident reports usually state the facts first, so this was accepted. On the full corpus, the share of unclustered incidents is about the same across description lengths (47% to 53%), which suggests truncation is not driving the results.

---

## 8. PCA

**Recipe:** `compute_HI_ALL_PCA` · **Input:** `HI_ALL_EMBEDDINGS` · **Output:** `HI_ALL_PCA`

**What it does.** Compresses the 768 dimensions to 120, keeping most of the information and removing redundancy and noise.

**Steps:**

1. **L2 normalisation** of the embeddings. The model compares texts by angle (cosine similarity); after normalisation, plain Euclidean distance gives the same ranking, which is what the downstream algorithms expect.
2. **PCA** to `NB_COMPONENTS = 120`, `random_state = 42`.
3. **L2 normalisation** of the PCA output again, so the geometry stays consistent with cosine similarity.

**Check:** variance explained by the 120 components = **[TBC]**. Target window: 0.75 to 0.90. (2025 corpus: 0.8064 with 100 components.)

**Output columns:** `LB_REF`, `LB_DESC_EN`, `pca_0` … `pca_119`.

---

## 9. UMAP 2D (visualisation)

**Recipe:** `compute_HI_ALL_UMAP` [TBC] · **Input:** `HI_ALL_PCA` · **Output:** `HI_ALL_UMAP`

**What it does.** Projects every incident onto a 2D map where incidents with similar meaning sit close together. **This map is for people, not for the algorithm**: squeezing hundreds of thousands of points onto two dimensions distorts distances enough to create groups that do not exist, so the clustering never runs on it.

**Configuration:**

| Parameter | Value | Why |
|---|---|---|
| `n_neighbors` | 15 | balance between local and global structure |
| `min_dist` | 0.1 | spreads points enough to be readable |
| `metric` | `euclidean` | input is already L2-normalised |
| `n_components` | 2 | |
| `random_state` | 42 | reproducible map |

**Note on run time.** Setting `random_state` forces UMAP to run single-threaded. On 357k incidents this made the run very long. For a future run, dropping the seed and setting `n_jobs=-1`, `low_memory=True` speeds it up considerably; only the orientation of the map changes.

**Output columns:** `LB_REF`, `LB_DESC_EN`, `umap_x`, `umap_y`.

---

## 10. UMAP 10D (clustering space)

**Recipe:** `compute_HI_ALL_UMAP_10D` · **Input:** `HI_ALL_PCA` · **Output:** `HI_ALL_UMAP_10D`

**What it does.** A second UMAP projection, to 10 dimensions, built specifically for clustering. It keeps enough dimensions to preserve the real structure while strengthening the density contrasts that HDBSCAN relies on.

**Configuration:**

| Parameter | Value | Why |
|---|---|---|
| `n_components` | 10 | 10D gave better clusters than 15D on the 2025 corpus |
| `n_neighbors` | 15 | same as the 2D map |
| `min_dist` | 0.0 | packs similar points tightly: the right setting before clustering |
| `metric` | `euclidean` | same geometry as the 2D map |
| `low_memory`, `n_jobs` | `True`, `-1` | parallel run |
| Fit sample | 100,000 random incidents (seed 42) | fitting is the expensive part |
| Transform | full corpus, chunks of 50,000 | keeps memory under control |

**Reproducibility.** No `random_state` is set on UMAP itself (that would force single-threading). Instead, the 10D coordinates are **frozen in a dataset**: the sweep and the clustering both read the same coordinates, so clustering can be re-run in minutes without recomputing UMAP.

**Check performed.** Incidents used to fit UMAP and incidents only transformed show the same unclustered rate (48.8% vs 48.7%), so fitting on a subset does not bias the result.

**Output columns:** `LB_REF`, `u10_0` … `u10_9`.

---

## 11. Clustering

### 11.1 Why HDBSCAN and not k-means

The reference paper uses k-means. We tested it on the 2025 corpus for every number of clusters from 4 to 20:

| Metric | Result | Reading |
|---|---|---|
| Silhouette | 0.078 – 0.093 | below 0.10 means no detectable structure |
| Davies-Bouldin | 2.7 – 3.1 | should be below 1 |
| Calinski-Harabasz | steady decline, no peak | no natural number of clusters |
| Inertia | straight line, no elbow | same |

K-means assumes round groups of similar size. Our corpus is a large diffuse mass surrounded by many small dense groups, which is the opposite. **HDBSCAN** works on density instead: it handles groups of very different sizes, finds the number of clusters by itself, and labels incidents that belong to no group as noise (`-1`) instead of forcing them into one. On the same 2025 data, silhouette rose from 0.09 to 0.63.

### 11.2 Parameter sweep

**Recipe:** `compute_HI_ALL_HDBSCAN_SWEEP` · **Output:** `HI_ALL_HDBSCAN_SWEEP`

Testing every configuration on 357k incidents is too slow, so the sweep runs on a **stratified sample of 60,000 incidents** (stratified by Basel event type, so the sample keeps the corpus composition).

**Parameters swept:**

| Parameter | Meaning | Values tested |
|---|---|---|
| `min_cluster_size` | smallest group allowed to be a family | 150, 300, 500, 800, 1,200 (full-corpus scale) |
| `min_samples` | how conservative the density estimate is | 5, 10, 15 |
| `cluster_selection_method` | `eom` keeps stable groups; `leaf` cuts into the finest pieces | `eom`, `leaf` |

`min_cluster_size` is expressed at full-corpus scale and converted to the sample (× 60,000 / 357,552).

**Result columns:**

| Column | Meaning |
|---|---|
| `n_clusters` | number of families found |
| `coverage_pct` / `noise_pct` | share of incidents assigned to a family / left as noise |
| `silhouette` | separation of the families, computed on clustered points, on a 10,000-point subsample (the metric is too costly on the full set) |
| `size_min_full_est`, `size_median_full_est`, `size_max_full_est` | family sizes projected back to the full corpus |
| `max_share_pct` | share of the corpus held by the largest family (guards against one catch-all family) |

**Acceptance criteria:** 60–400 families, largest family under 10% of the corpus, noise under 40%, smallest family of at least 100 incidents.

### 11.3 Full-corpus check

The sample suggested lower noise than the full run produced, so five configurations were re-run directly on the 357k incidents:

| `min_cluster_size` | `min_samples` | Clusters | Noise | Silhouette | Median size | Largest family |
|---|---|---|---|---|---|---|
| 500 | 10 | 107 | 48.7% | — | — | — |
| 500 | 5 | 106 | 49.4% | 0.581 | 1,118 | 4.17% |
| 500 | 3 | 117 | 50.3% | 0.571 | 1,057 | 3.72% |
| 300 | 10 | 200 | 45.5% | **0.618** | 566 | [TBC] |
| 300 | 5 | 201 | 49.3% | 0.586 | 520 | 2.7% |
| 200 | 5 | 295 | 47.2% | 0.604 | 391 | 2.7% |

**Reading.** The noise rate barely moves whatever the parameters (45% to 50%). It is therefore not a tuning problem: on a large, continuous space, HDBSCAN labels as noise the points that detach from a group before it splits into families. Two checks confirm this:

- noise is the same for UMAP-fitted and UMAP-transformed incidents (section 10);
- noise is the same across description lengths (section 7).

### 11.4 Selected configuration

| Parameter | Value |
|---|---|
| Clustering space | `HI_ALL_UMAP_10D` |
| `min_cluster_size` | **500** [TBC — 300 is the best-scoring alternative] |
| `min_samples` | 10 |
| `cluster_selection_method` | `eom` |
| `algorithm` | `boruvka_kdtree`, `approx_min_span_tree=True` (fast in low dimensions) |

### 11.5 Re-attaching unclustered incidents

[TBC — confirm this step is implemented in the current recipe.]

About half of the incidents are left as noise. Most of them sit near a family: for 93% of them, at least 8 of their 10 nearest clustered neighbours belong to the same family. They are re-attached only if **two conditions** hold:

1. **Agreement:** at least 80% of the 10 nearest clustered neighbours belong to the same family.
2. **Proximity:** the incident is no further from those neighbours than family members typically are from each other (95th percentile of the in-family neighbourhood radius).

Agreement alone is not enough: an isolated incident far from everything can still have its 10 nearest neighbours in one family.

Each incident then falls into one of three tiers:

| Tier | Meaning |
|---|---|
| `CORE` | assigned by HDBSCAN |
| `EXTENDED` | re-attached, with both guarantees |
| `UNASSIGNED` | genuinely isolated |

Cluster profiles are built on `CORE` incidents only, so the description of each family is not diluted by borderline incidents.

### 11.6 Scope filter: excluding *Closed* incidents

Incidents with status *Closed* (~42,000) are excluded with an **inner join on `LB_REF`**, applied to `HI_ALL_UMAP_10D` at the entrance of the clustering recipe.

Translation, embedding, PCA and UMAP are **not** recomputed. An incident's embedding does not depend on the other incidents, and the status is a workflow attribute that does not change how an incident is described, so removing these incidents does not distort the space.

Everything from the clustering onward **is** re-run: clustering, profiles, LLM labelling, map and loss aggregation. Cluster numbers change between runs, so labels from a previous run cannot be reused.

---

## 12. Output datasets: column dictionary

### `HI_ALL_INCIDENTS_CLUSTERED` — one row per incident

| Column | Meaning |
|---|---|
| `LB_REF` | incident reference |
| `cluster` | family number; `-1` = noise |
| `membership` | 0–1, how firmly the incident belongs to its family (0.95 = heart of the family, 0.4 = edge) |
| `cluster_assigned` | family after re-attachment (equal to `cluster` for core incidents) |
| `assignment_confidence` | share of the 10 nearest clustered neighbours in the assigned family; 1.0 for core incidents |
| `assignment_tier` | `CORE`, `EXTENDED` or `UNASSIGNED` |
| `dist_ratio` | distance to the family relative to the typical family radius; ≤ 1 = within the family's usual spread |
| `is_core` | `True` if assigned by HDBSCAN |
| `LB_DESC_EN` | English description |
| `umap_x`, `umap_y` | coordinates on the 2D map |
| `CD_EVENT_TYPE`, `event_type_label` | Basel event type, code and label |
| `incident_description_cleaned` | lemmatised text, used for the cluster terms |
| `year` | incident year [TBC date column name] |
| `desc_length` | description length in characters |

### `HI_ALL_CLUSTER_PROFILES` — one row per family

| Column | Meaning | How to read it |
|---|---|---|
| `cluster` | family number | |
| `size`, `share_pct` | core incidents, and share of the corpus | drives prioritisation |
| `size_with_extended` | size once re-attached incidents are counted | |
| `top_terms` | the 12 most **distinctive** terms (how much more often a term appears in the family than in the whole corpus), from the cleaned text | lets you name a family without reading every description |
| `n_unique_descriptions`, `repetition_factor` | distinct wordings, and incidents per wording | 1.0 = every description differs, so the family groups meaning, not copies; a high value means templated text |
| `mean_membership`, `quality_flag` | average belonging; `STRONG` ≥ 0.75, `MEDIUM` ≥ 0.55, else `WEAK` | review strong families first |
| `dominant_event_type`, `event_type_purity` | main Basel category and its share in the family | 1.0 = perfectly aligned with one category |
| `n_event_types` | number of Basel categories in the family | |
| `taxonomy_relation` | `ALIGNED` (purity ≥ 0.85), `PARTIAL` (≥ 0.60), `CROSS_CUTTING` (below) | `CROSS_CUTTING` = a pattern the Basel taxonomy cannot express |
| `year_min`, `year_max`, `year_median`, `year_iqr`, `temporal_flag` | time span of the family; `TIME_CONCENTRATED` if the interquartile range is ≤ 2 years | a time-concentrated family may reflect an era (system, product, wording habit) rather than a lasting root cause |
| `mean_desc_length` | average description length | |
| `example_1` … `example_5`, with `example_N_ref` | the 5 most representative incidents (highest membership), with their references | material for analyst review |
| `analyst_label`, `analyst_comment` | empty, filled during validation | |

---

## 13. Known limitations

| Limitation | Impact | Status |
|---|---|---|
| Truncation at ~1,500 characters | the end of long descriptions is not encoded | accepted; not linked to the noise rate |
| Untranslated residue | a family may form on language rather than meaning (seen once on the 2025 corpus, 292 incidents) | [TBC on the full corpus]; to fix before industrialisation |
| ~45–50% of incidents left as noise by HDBSCAN | structural effect of density clustering at this scale | mitigated by the two-condition re-attachment |
| 27 years of history | families may group incidents of the same era rather than the same cause | monitored with `temporal_flag` [TBC result] |
| Model access | installed from a GitHub mirror as a tactical workaround | target: official ModelHub access |

---

## 14. How to re-run the flow

| What changed | What to re-run |
|---|---|
| New or updated incidents | the whole flow, from translation onward, for the new incidents |
| Scope reduced to a subset of already-processed incidents | inner join on `HI_ALL_UMAP_10D`, then clustering and everything downstream |
| Clustering parameters only | clustering and everything downstream; UMAP 10D is reused as is |
| New embedding model | embedding and everything downstream |

Downstream of the clustering (outside the scope of this page): LLM labelling of each family, the interactive map `cluster_map_all.html` in the managed folder, and the aggregation of losses and provisions per family.

---

## 15. Decision log

| Decision | Reason |
|---|---|
| Sentence embeddings instead of word2vec | better on long, varied descriptions; available in the environment |
| `all-mpnet-base-v2` instead of a multilingual model | the corpus is translated to English upstream; English-specialised models perform better on English text |
| Translate before embedding | the model is English-only; without it, incidents were grouped by language |
| HDBSCAN instead of k-means | k-means found no structure (silhouette < 0.10) |
| Cluster on UMAP 10D, never on 2D | 2D distorts distances and creates artificial groups |
| Freeze the 10D space in a dataset | reproducibility, and fast re-runs of the clustering |
| Re-attachment with distance check | an agreement vote alone would attach isolated incidents |
| Exclude *Closed* incidents without recomputing PCA / UMAP | status does not change the meaning of a description |

---

## 16. Values to confirm

- Exact incident count after excluding *Closed* incidents.
- Language distribution and untranslated residue on the full corpus.
- Name of the embedding recipe and the encoding batch size.
- Variance explained by the 120 PCA components.
- Name of the UMAP 2D recipe.
- Final `min_cluster_size` (500 or 300) and the matching cluster count, noise rate and silhouette.
- Whether the two-condition re-attachment is implemented in the current recipe, and the resulting coverage.
- Name of the incident date column, and the result of the temporal check.
