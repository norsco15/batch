# --------------------
# Output + main
# --------------------
def write_metrics_to_excel(metrics: list[tuple[str, float]], output_path: Union[str, Path]) -> None:
    pd.DataFrame(metrics, columns=["Indicator", "Value"]).to_excel(output_path, index=False, engine="openpyxl")


    write_metrics_to_excel(metrics, output_path)
