private CellStyle createCellStyle(SCMExtractionCellStyleEntity cellStyleEntity, Workbook workbook) {
    CellStyle style = workbook.createCellStyle();

    // Couleurs de fond et de texte
    if (cellStyleEntity.getBackgroundColor() != null) {
        style.setFillForegroundColor(IndexedColors.valueOf(cellStyleEntity.getBackgroundColor()).getIndex());
        style.setFillPattern(FillPatternType.SOLID_FOREGROUND);
    }

    if (cellStyleEntity.getForegroundColor() != null) {
        Font font = workbook.createFont();
        font.setColor(IndexedColors.valueOf(cellStyleEntity.getForegroundColor()).getIndex());
        style.setFont(font);
    }

    // Alignement horizontal et vertical
    if (cellStyleEntity.getHorizontalAlignment() != null) {
        style.setAlignment(HorizontalAlignment.valueOf(cellStyleEntity.getHorizontalAlignment().toUpperCase()));
    }

    if (cellStyleEntity.getVerticalAlignment() != null) {
        style.setVerticalAlignment(VerticalAlignment.valueOf(cellStyleEntity.getVerticalAlignment().toUpperCase()));
    }

    // Style des bordures
    if (cellStyleEntity.getBorderStyle() != null) {
        BorderStyle borderStyle = BorderStyle.valueOf(cellStyleEntity.getBorderStyle().toUpperCase());
        style.setBorderBottom(borderStyle);
        style.setBorderTop(borderStyle);
        style.setBorderLeft(borderStyle);
        style.setBorderRight(borderStyle);
    }

    // Police (nom, taille, emphase)
    Font font = workbook.createFont();
    if (cellStyleEntity.getFontName() != null) {
        font.setFontName(cellStyleEntity.getFontName());
    }

    if (cellStyleEntity.getFontHeight() != null) {
        font.setFontHeightInPoints(cellStyleEntity.getFontHeight().shortValue());
    }

    if (cellStyleEntity.getFontTypographicEmphasis() != null) {
        if ("BOLD".equalsIgnoreCase(cellStyleEntity.getFontTypographicEmphasis())) {
            font.setBold(true);
        }
        if ("ITALIC".equalsIgnoreCase(cellStyleEntity.getFontTypographicEmphasis())) {
            font.setItalic(true);
        }
    }

    style.setFont(font);

    return style;
}
