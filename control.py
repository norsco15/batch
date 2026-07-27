import dataiku
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 90)

prof = dataiku.Dataset("cluster_profiles").get_dataframe()

cols = ["cluster", "size", "repetition_factor", "event_type_purity",
        "n_event_types", "dominant_event_type", "top_terms"]

print(prof[cols].head(20).to_string(index=False))