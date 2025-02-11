private SFCMExtractionCSVEntity mapJsonExtractionCSVToExtractionCSVEntity(JSonExtractionCSV json) {
    if (json == null) {
        return null;
    }
    SFCMExtractionCSVEntity csvEntity = new SFCMExtractionCSVEntity();
    csvEntity.setExtractionCSVId(json.getExtractionCSVId());
    csvEntity.setExtractionCSVHeader(json.getExtractionCSVHeader());
    csvEntity.setExtractionCSVSeparator(json.getExtpactionCSVSeparator());
    csvEntity.setExtractionDateFormat(json.getExtractionDateFormat());
    csvEntity.setExtractionNumberFormat(json.getExtractionNumberFormat());

    // Nouveau bloc :
    if (json.getJsonExtractionCSVFormat() != null) {
        SFCMExtractionCSVFormatEntity formatEntity = mapJsonExtractionCSVFormatToExtractionCSVFormatEntity(json.getJsonExtractionCSVFormat());
        csvEntity.setExtractionCSVFormatEntity(formatEntity);
        formatEntity.setExtractionCSVEntity(csvEntity);
    }

    return csvEntity;
}

private SFCMExtractionCSVFormatEntity mapJsonExtractionCSVFormatToExtractionCSVFormatEntity(JSonExtractionCSVFormat jsonFormat) {
    if (jsonFormat == null) {
        return null;
    }
    SFCMExtractionCSVFormatEntity formatEntity = new SFCMExtractionCSVFormatEntity();
    formatEntity.setExtractionCSVFormatId(jsonFormat.getExtractionCSVFormatId());
    formatEntity.setExcludedHeaders(jsonFormat.getExcludedHeaders());
    // On ne set pas extractionCSVEntity ici, car on le fait après coup (pour la relation bidir)
    return formatEntity;
}
