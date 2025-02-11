private JSonExtractionCSV mapSFCMExtractionCSVEntityToJSonExtractionCSV(SFCMExtractionCSVEntity entity) {
    if (entity == null) {
        return null;
    }
    JSonExtractionCSV json = new JSonExtractionCSV();
    json.setExtractionCSVId(entity.getExtractionCSVId());
    json.setExtractionCSVHeader(entity.getExtractionCSVHeader());
    json.setExtpactionCSVSeparator(entity.getExtractionCSVSeparator());
    json.setExtractionDateFormat(entity.getExtractionDateFormat());
    json.setExtractionNumberFormat(entity.getExtractionNumberFormat());

    // SQL existant
    if (entity.getExtractionSQLEntity() != null) {
        json.setJsonExtractionSQL(mapSFCMExtractionSQLEntityToJSonExtractionSQL(entity.getExtractionSQLEntity()));
    }

    // Nouveau bloc :
    if (entity.getExtractionCSVFormatEntity() != null) {
        json.setJsonExtractionCSVFormat(
            mapSFCMExtractionCSVFormatEntityToJSonExtractionCSVFormat(entity.getExtractionCSVFormatEntity())
        );
    }

    return json;
}

private JSonExtractionCSVFormat mapSFCMExtractionCSVFormatEntityToJSonExtractionCSVFormat(SFCMExtractionCSVFormatEntity formatEntity) {
    if (formatEntity == null) {
        return null;
    }
    JSonExtractionCSVFormat jsonFormat = new JSonExtractionCSVFormat();
    jsonFormat.setExtractionCSVFormatId(formatEntity.getExtractionCSVFormatId());
    jsonFormat.setExcludedHeaders(formatEntity.getExcludedHeaders());
    return jsonFormat;
}
