import dataiku

df = dataiku.Dataset("incidents_cleaned_final").get_dataframe()
COL = "incident_description_en_pre_cleaning"

lengths = df[COL].fillna("").str.len()
for threshold in [1500, 2000, 3000]:
    n = (lengths > threshold).sum()
    print(f"> {threshold} chars : {n} incidents ({n/len(df):.1%})")