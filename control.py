import dataiku
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tempfile
import os

ID_COL, DESC_COL, EVENT_COL = "LB_REF", "LB_DESC", "CD_EVENT_TYPE"

df = dataiku.Dataset("incidents_clustered").get_dataframe()
prof = dataiku.Dataset("cluster_profiles").get_dataframe()

# Attach cluster-level context so it shows up on hover
df = df.merge(
    prof[["cluster", "size", "top_terms", "repetition_factor", "analyst_label"]],
    on="cluster", how="left"
)

# Legend label: cluster id + size (+ analyst label once filled in)
df["cluster_name"] = df.apply(
    lambda r: f"C{int(r['cluster'])} ({int(r['size'])})"
    if pd.notna(r["size"]) and str(r.get("analyst_label", "")).strip() == ""
    else (f"C{int(r['cluster'])} — {r['analyst_label']}" if pd.notna(r["size"]) else "Noise"),
    axis=1,
)

# Wrap the description so the tooltip stays readable
def wrap(text, width=90, max_chars=600):
    t = str(text)[:max_chars]
    lines, cur = [], ""
    for w in t.split():
        if len(cur) + len(w) + 1 > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return "<br>".join(lines)

df["hover_desc"] = df[DESC_COL].apply(wrap)
df["hover_terms"] = df["top_terms"].fillna("").apply(lambda t: wrap(t, width=70, max_chars=200))

core = df[df["cluster"] != -1].copy()
noise = df[df["cluster"] == -1].copy()

# Sort legend by cluster size (largest first)
order = (core.groupby("cluster_name")["size"].first()
             .sort_values(ascending=False).index.tolist())

fig = px.scatter(
    core,
    x="umap_x", y="umap_y",
    color="cluster_name",
    category_orders={"cluster_name": order},
    custom_data=[ID_COL, "hover_desc", "hover_terms", EVENT_COL, "cluster", "size"],
    width=1600, height=950,
    title=(f"MLION — {core['cluster'].nunique()} root-cause families "
           f"({len(core)} incidents clustered, {len(noise)} unclustered)"),
)
fig.update_traces(
    marker=dict(size=5, opacity=0.8, line=dict(width=0)),
    hovertemplate=(
        "<b>%{customdata[0]}</b> — cluster %{customdata[4]} "
        "(%{customdata[5]} incidents)<br>"
        "Event type: %{customdata[3]}<br>"
        "<i>Cluster terms:</i> %{customdata[2]}<br><br>"
        "%{customdata[1]}<extra></extra>"
    ),
)

# Noise as a faint grey layer, hidden by default (toggle in legend)
if len(noise):
    fig.add_trace(go.Scattergl(
        x=noise["umap_x"], y=noise["umap_y"],
        mode="markers", name="Unclustered",
        marker=dict(size=3, color="lightgrey", opacity=0.35),
        visible="legendonly", hoverinfo="skip",
    ))

fig.update_layout(
    hoverlabel=dict(bgcolor="white", font_size=12, align="left"),
    legend=dict(itemsizing="constant", font=dict(size=10),
                title="Clusters (by size)"),
    xaxis_title=None, yaxis_title=None,
    plot_bgcolor="white",
)
fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False)

folder = dataiku.Folder("vectorization_artifacts")
with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as t:
    tmp = t.name
try:
    # include_plotlyjs=True -> fully standalone (~4 MB), no CDN dependency.
    # Safer inside the bank network; switch to "cdn" for a lighter file.
    fig.write_html(tmp, include_plotlyjs=True)
    with open(tmp, "rb") as f:
        folder.upload_stream("cluster_map.html", f)
    print("Uploaded cluster_map.html")
finally:
    os.remove(tmp)