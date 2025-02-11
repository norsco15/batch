private FlatFileItemWriter<Map<String, Object>> csvWriter(SFCMExtractionEntity entity) {
    FlatFileItemWriter<Map<String, Object>> writer = new FlatFileItemWriter<>();
    writer.setEncoding("UTF-8");
    writer.setResource(new FileSystemResource("output/" + getExtractionCsvFileName(entity.getExtractionName())));
    // ...
    String separator = entity.getExtractionCSVEntity().getExtractionCSVSeparator();
    String header = entity.getExtractionCSVEntity().getExtractionCSVHeader();
    SimpleDateFormat dateFormatter = getDateFormatter(entity.getExtractionCSVEntity().getExtractionDateFormat());
    DecimalFormat numberFormatter = getDecimalFormatter(entity.getExtractionCSVEntity().getExtractionNumberFormat());

    // **Nouveau** : récupérer excludedHeaders
    Set<String> excludedHeadersSet = new HashSet<>();
    SFCMExtractionCSVFormatEntity formatEntity = entity.getExtractionCSVEntity().getExtractionCSVFormatEntity();
    if (formatEntity != null && formatEntity.getExcludedHeaders() != null) {
        // exemple: "EVENT_ID;LOAN_ID"
        excludedHeadersSet = Arrays.stream(formatEntity.getExcludedHeaders().split(";"))
                                   .map(String::trim)
                                   .collect(Collectors.toSet());
    }

    writer.setHeaderCallback(writerCallback -> {
        if (header != null) {
            writerCallback.write(header);
        }
    });

    writer.setLineAggregator(item -> {
        if (header != null) {
            String[] columns = header.split(separator);
            StringBuilder line = new StringBuilder();
            for (String column : columns) {
                // attention : vous faites uppercase ou pas ?
                String key = column.trim().toUpperCase();
                Object value = item.get(key); // map col => val
                // On exécute le formattage si ce n'est pas dans la liste "excluded"
                if (value instanceof BigDecimal && !excludedHeadersSet.contains(column.trim())) {
                    value = numberFormatter.format(value);
                } 
                // etc. pour Date...
                line.append(value != null ? value : "").append(separator);
            }
            return line.substring(0, line.length() - 1);
        } else {
            // fallback...
            StringBuilder line = new StringBuilder();
            item.forEach((k, v) -> line.append(v).append(separator));
            return line.substring(0, line.length() - 1);
        }
    });
    return writer;
}
