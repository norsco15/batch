from pptx import Presentation
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

def create_progress_ppt(df):

    prs = Presentation()
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    top = Inches(1)

    for index, row in df.iterrows():

        label = str(index)
        progress = row['Average completion rate (%)']

        # Texte
        textbox = slide.shapes.add_textbox(
            Inches(0.5),
            top,
            Inches(4),
            Inches(0.4)
        )

        textbox.text = label

        # Barre grise (background)
        bg_bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(4.5),
            top,
            Inches(4),
            Inches(0.3)
        )

        bg_bar.fill.solid()
        bg_bar.fill.fore_color.rgb = RGBColor(220,220,220)
        bg_bar.line.fill.background()

        # Barre verte (progress)
        width = 4 * progress / 100

        progress_bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(4.5),
            top,
            Inches(width),
            Inches(0.3)
        )

        progress_bar.fill.solid()
        progress_bar.fill.fore_color.rgb = RGBColor(0,176,80)
        progress_bar.line.fill.background()

        # Pourcentage
        percent_box = slide.shapes.add_textbox(
            Inches(8.7),
            top,
            Inches(1),
            Inches(0.3)
        )

        percent_box.text = f"{progress}%"

        top += Inches(0.6)

    prs.save("progress_report.pptx")