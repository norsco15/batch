import math
import pandas as pd
from datetime import datetime

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR
from pptx.dml.color import RGBColor


def format_date_for_excel(value):
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value)
    except Exception:
        return None


def format_date_for_ppt(value):
    if pd.isna(value) or value is None:
        return "N/A"
    try:
        dt = pd.to_datetime(value)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return str(value)


def safe_text(value, default="N/A"):
    if value is None or pd.isna(value):
        return default
    text = str(value).strip()
    return text if text else default


def compute_metrics(
    input_file="all_ipt.xlsx",
    excel_output="ipt_metrics.xlsx",
    ppt_output="ipt_progress_report.pptx"
):
    # Lecture source
    ipt_all = pd.read_excel(input_file)

    # Normalisation minimale des colonnes attendues
    expected_columns = [
        "State",
        "Local risk reference",
        "Percent Complete",
        "Planned end date",
        "Risk Owner/Sponsor",
        "Residual risk level",
        "Title",
    ]
    missing = [c for c in expected_columns if c not in ipt_all.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le fichier source: {missing}")

    # Conversion types
    ipt_all["Percent Complete"] = pd.to_numeric(
        ipt_all["Percent Complete"], errors="coerce"
    ).fillna(0)

    ipt_all["Planned end date"] = pd.to_datetime(
        ipt_all["Planned end date"], errors="coerce"
    )

    # Split open / closed
    ipt_closed = ipt_all[ipt_all["State"] == "Closed Complete"].copy()
    ipt_open = ipt_all[ipt_all["State"] != "Closed Complete"].copy()

    # Liste des RL
    rls_closed = set(ipt_closed["Local risk reference"].dropna().unique())
    rls_open = set(ipt_open["Local risk reference"].dropna().unique())
    all_rls = sorted(rls_closed.union(rls_open))

    results = {}

    for rl in all_rls:
        closed_subset = ipt_closed[ipt_closed["Local risk reference"] == rl]
        open_subset = ipt_open[ipt_open["Local risk reference"] == rl]

        closed_count = closed_subset.shape[0]
        open_count = open_subset.shape[0]
        total = closed_count + open_count

        # Progression moyenne :
        # - actions closed = 100
        # - actions open = valeur Percent Complete
        completions_open = open_subset["Percent Complete"].tolist()
        completions_closed = [100] * closed_count
        all_completions = completions_open + completions_closed
        avg_completion = round(sum(all_completions) / len(all_completions), 2) if all_completions else 0

        # Ratio open actions type 11/45
        ratio_open = f"{open_count}/{total}" if total > 0 else "0/0"

        # Latest planned end date uniquement sur open
        planned_dates = open_subset["Planned end date"].dropna()
        latest_planned_end_date = planned_dates.max() if not planned_dates.empty else None

        # Sample row pour récupérer des infos stables
        sample_row = pd.concat([open_subset, closed_subset], ignore_index=True).head(1)

        risk_owner = safe_text(
            sample_row["Risk Owner/Sponsor"].iloc[0] if not sample_row.empty else None
        )
        residual_level = safe_text(
            sample_row["Residual risk level"].iloc[0] if not sample_row.empty else None
        )
        title = safe_text(
            sample_row["Title"].iloc[0] if not sample_row.empty else rl
        )

        results[rl] = {
            "Local risk reference": rl,
            "Title": title,
            "Open actions ratio": ratio_open,
            "Average completion rate (%)": avg_completion,
            "Latest planned end date": latest_planned_end_date,
            "Risk Owner/Sponsor": risk_owner,
            "Residual risk level": residual_level,
        }

    df_results = pd.DataFrame.from_dict(results, orient="index").reset_index(drop=True)

    # Export Excel
    with pd.ExcelWriter(excel_output, engine="openpyxl") as writer:
        df_results.to_excel(writer, sheet_name="Metrics", index=False)

    # Export PowerPoint
    create_progress_ppt(df_results, ppt_output)

    print(f"Excel généré : {excel_output}")
    print(f"PowerPoint généré : {ppt_output}")

    return df_results


def add_textbox(slide, left, top, width, height, text,
                font_size=12, bold=False,
                font_color=RGBColor(0, 0, 0),
                align=PP_ALIGN.LEFT,
                vertical_anchor=MSO_VERTICAL_ANCHOR.MIDDLE):
    textbox = slide.shapes.add_textbox(left, top, width, height)
    text_frame = textbox.text_frame
    text_frame.clear()
    text_frame.word_wrap = True
    text_frame.vertical_anchor = vertical_anchor

    p = text_frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = str(text)
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = font_color

    return textbox


def create_progress_ppt(df, output_file):
    prs = Presentation()
    prs.slide_width = Inches(13.333)   # format 16:9
    prs.slide_height = Inches(7.5)

    rows_per_slide = 10

    # Layout
    title_top = Inches(0.25)
    title_left = Inches(0.4)

    first_row_top = Inches(1.0)
    row_height = Inches(0.56)

    label_left = Inches(0.45)
    label_width = Inches(6.0)

    bar_left = Inches(6.25)
    bar_width = Inches(4.8)
    bar_height = Inches(0.28)

    date_left = Inches(11.2)
    date_width = Inches(1.6)

    # Couleurs
    bar_bg_color = RGBColor(230, 230, 230)
    bar_fill_color = RGBColor(0, 176, 80)
    text_dark = RGBColor(0, 0, 0)
    text_light = RGBColor(255, 255, 255)
    teal_line = RGBColor(0, 153, 153)

    total_rows = len(df)
    total_slides = max(1, math.ceil(total_rows / rows_per_slide))

    for slide_index in range(total_slides):
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        # Titre slide
        add_textbox(
            slide,
            title_left,
            title_top,
            Inches(6),
            Inches(0.4),
            f"Action Plans Progress - Part {slide_index + 1}",
            font_size=20,
            bold=True,
            font_color=text_dark
        )

        # Ligne décorative
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.4),
            Inches(0.75),
            Inches(12.2),
            Inches(0.04)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = teal_line
        line.line.fill.background()

        start = slide_index * rows_per_slide
        end = min(start + rows_per_slide, total_rows)
        df_chunk = df.iloc[start:end]

        for i, (_, row) in enumerate(df_chunk.iterrows()):
            current_top = first_row_top + i * row_height

            title_text = safe_text(row.get("Title", "N/A"))
            progress = float(row.get("Average completion rate (%)", 0) or 0)
            progress = max(0, min(100, progress))
            planned_end_date = format_date_for_ppt(row.get("Latest planned end date"))

            # Titre
            add_textbox(
                slide,
                label_left,
                current_top,
                label_width,
                Inches(0.38),
                title_text,
                font_size=11,
                bold=False,
                font_color=text_dark,
                align=PP_ALIGN.LEFT
            )

            # Fond barre
            bg_bar = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                bar_left,
                current_top + Inches(0.03),
                bar_width,
                bar_height
            )
            bg_bar.fill.solid()
            bg_bar.fill.fore_color.rgb = bar_bg_color
            bg_bar.line.fill.background()

            # Barre progression
            progress_width = max(Inches(0.01), bar_width * (progress / 100.0))
            fg_bar = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                bar_left,
                current_top + Inches(0.03),
                progress_width,
                bar_height
            )
            fg_bar.fill.solid()
            fg_bar.fill.fore_color.rgb = bar_fill_color
            fg_bar.line.fill.background()

            # Pourcentage à l'intérieur de la barre
            # centré dans toute la zone de barre pour rester lisible
            percent_text = f"{progress:.2f}".rstrip("0").rstrip(".") + "%"
            add_textbox(
                slide,
                bar_left,
                current_top + Inches(0.01),
                bar_width,
                Inches(0.32),
                percent_text,
                font_size=10,
                bold=True,
                font_color=text_light if progress >= 15 else text_dark,
                align=PP_ALIGN.CENTER
            )

            # Date à droite
            add_textbox(
                slide,
                date_left,
                current_top,
                date_width,
                Inches(0.38),
                planned_end_date,
                font_size=10,
                bold=False,
                font_color=text_dark,
                align=PP_ALIGN.LEFT
            )

    prs.save(output_file)


if __name__ == "__main__":
    compute_metrics(
        input_file="all_ipt.xlsx",
        excel_output="ipt_metrics.xlsx",
        ppt_output="ipt_progress_report.pptx"
    )