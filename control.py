# Map Basel codes to their business labels; unmapped codes fall back to the code
final[EVENT_LABEL_COL] = (
    final[EVENT_COL].map(EVENT_TYPE_LABELS).fillna(final[EVENT_COL])
)

unmapped = sorted(set(final.loc[final[EVENT_COL].notna(), EVENT_COL]) - set(EVENT_TYPE_LABELS))
if unmapped:
    print(f"WARNING: no label for {len(unmapped)} event type(s): {unmapped}")




============

# Event type distribution -> reveals cross-taxonomy patterns
    et = sub[EVENT_LABEL_COL].value_counts()
    purity = float(et.iloc[0] / n) if len(et) else np.nan

======

"dominant_event_type": et.index[0] if len(et) else None,

=====

"n_event_types": int(sub[EVENT_LABEL_COL].nunique()),


====

df = df.merge(
    prof[["cluster", "size", "share_pct", "top_terms", "repetition_factor",
          "quality_flag", "taxonomy_relation", "analyst_label"]],
    on="cluster", how="left"
)


====

# Legend label: "C50 (819 — 8.2%)" or "C50 — KYC recertification (819 — 8.2%)"
def make_name(r):
    if pd.isna(r["size"]):
        return "Noise"
    cid = int(r["cluster"])
    stats = f"{int(r['size'])} — {r['share_pct']:.1f}%"
    label = r.get("analyst_label")
    label = "" if pd.isna(label) else str(label).strip()
    return f"C{cid} — {label} ({stats})" if label else f"C{cid} ({stats})"

df["cluster_name"] = df.apply(make_name, axis=1)


=====


custom_data=[ID_COL, "hover_desc", "hover_terms", EVENT_LABEL_COL,
                 "cluster", "size", "share_pct", "quality_flag", "taxonomy_relation"],


====

hovertemplate=(
        "<b>%{customdata[0]}</b> — cluster %{customdata[4]}<br>"
        "Family size: %{customdata[5]} incidents (%{customdata[6]:.1f}% of corpus)<br>"
        "Quality: %{customdata[7]} | Taxonomy: %{customdata[8]}<br>"
        "Event type: %{customdata[3]}<br>"
        "<i>Cluster terms:</i> %{customdata[2]}<br><br>"
        "%{customdata[1]}<extra></extra>"
    ),


=====

title=(f"MLION — {core['cluster'].nunique()} root-cause families | "
           f"{len(core)} incidents clustered ({len(core)/len(df):.1%}), "
           f"{len(noise)} unclustered"),