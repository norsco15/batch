package com.example.batch.writer;

import com.example.entities.*;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.batch.item.ItemWriter;

import java.io.FileOutputStream;
import java.io.IOException;
import java.math.BigInteger;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class ExcelEntityWriter implements ItemWriter<SFCMExtractionEntity> {

    private final String filePath;
    private final Map<BigInteger, CellStyle> cellStyleCache;

    public ExcelEntityWriter(String filePath) {
        this.filePath = filePath;
        this.cellStyleCache = new HashMap<>();
    }

    @Override
    public void write(List<? extends SFCMExtractionEntity> items) throws IOException {
        Workbook workbook = new XSSFWorkbook();

        for (SFCMExtractionEntity extraction : items) {
            for (SFCMExtractionSheetEntity sheetEntity : extraction.getExtractionSheetEntitys()) {
                Sheet sheet = workbook.createSheet(sheetEntity.getSheetName());

                // Ajouter les en-têtes
                Row headerRow = sheet.createRow(0);
                Set<SFCMExtractionSheetHeaderEntity> headers = sheetEntity.getExtractionSheetHeaderEntitys();
                int colIndex = 0;
                for (SFCMExtractionSheetHeaderEntity header : headers) {
                    Cell cell = headerRow.createCell(colIndex++);
                    cell.setCellValue(header.getHeaderName());
                    // Appliquer un style d'en-tête si nécessaire
                    cell.setCellStyle(createHeaderCellStyle(workbook));
                }

                // Ajouter les données
                int rowIndex = 1;
                Set<SFCMExtractionSheetFieldEntity> fields = sheetEntity.getExtractionSheetFieldEntity();
                for (SFCMExtractionSheetFieldEntity field : fields) {
                    Row dataRow = sheet.createRow(rowIndex++);
                    colIndex = 0;
                    for (SFCMExtractionSheetHeaderEntity header : headers) {
                        Cell cell = dataRow.createCell(colIndex++);
                        cell.setCellValue(getFieldValue(field, header));
                        // Appliquer le style défini dans l'entité
                        CellStyle cellStyle = getCellStyle(workbook, field.getExtractionCellStyleEntity());
                        cell.setCellStyle(cellStyle);
                    }
                }
            }
        }

        // Écrire dans le fichier
        try (FileOutputStream outputStream = new FileOutputStream(filePath)) {
            workbook.write(outputStream);
        }
        workbook.close();
    }

    private String getFieldValue(SFCMExtractionSheetFieldEntity field, SFCMExtractionSheetHeaderEntity header) {
        // Implémentez la logique pour obtenir la valeur du champ en fonction de l'en-tête
        // Par exemple, si le nom de l'en-tête correspond à un attribut du champ
        // Retournez la valeur appropriée
        return "ValeurExemple"; // Remplacez par la logique réelle
    }

    private CellStyle getCellStyle(Workbook workbook, SFCMExtractionCellStyleEntity styleEntity) {
        if (styleEntity == null) {
            return workbook.createCellStyle();
        }

        // Vérifier si le style a déjà été créé et mis en cache
        if (cellStyleCache.containsKey(styleEntity.getExtractionCellStyleId())) {
            return cellStyleCache.get(styleEntity.getExtractionCellStyleId());
        }

        CellStyle cellStyle = workbook.createCellStyle();

        // Appliquer les propriétés du style
        if (styleEntity.getBackgroundColor() != null) {
            cellStyle.setFillForegroundColor(IndexedColors.valueOf(styleEntity.getBackgroundColor()).getIndex());
            cellStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        }

        if (styleEntity.getHorizontalAlignment() != null) {
            cellStyle.setAlignment(HorizontalAlignment.valueOf(styleEntity.getHorizontalAlignment()));
        }

        if (styleEntity.getVerticalAlignment() != null) {
            cellStyle.setVerticalAlignment(VerticalAlignment.valueOf(styleEntity.getVerticalAlignment()));
        }

        if (styleEntity.getBorderStyle() != null) {
            BorderStyle borderStyle = BorderStyle.valueOf(styleEntity.getBorderStyle());
            cellStyle.setBorderTop(borderStyle);
            cellStyle.setBorderBottom(borderStyle);
            cellStyle.setBorderLeft(borderStyle);
            cellStyle.setBorderRight(borderStyle);
        }

        Font font = workbook.createFont();
        if (styleEntity.getFontName() != null) {
            font.setFontName(styleEntity.getFontName());
        }

        if (styleEntity.getFontColor() != null) {
            font.setColor(IndexedColors.valueOf(styleEntity.getFontColor()).getIndex());
        }

        if (styleEntity.getFontHeight() != null) {
            font.setFontHeightInPoints(styleEntity.getFontHeight().shortValue());
        }

        if (styleEntity.getFontTypographicEmphasis() != null) {
            switch (styleEntity.getFontTypographicEmphasis().toLowerCase()) {
                case "bold":
                    font.setBold(true);
                    break;
                case "italic":
                    font.setItalic(true);
                    break;
                // Ajoutez d'autres cas si nécessaire
            }
        }

        cellStyle.setFont(font);

        // Mettre en cache le style pour une utilisation ultérieure

::contentReference[oaicite:0]{index=0}

==========================================
        @Bean
        @StepScope
        public ExcelEntityWriter excelEntityWriter(
                @Value("#{jobParameters['extractionId']}") String extractionId) {

            String filePath = "output/extraction_" + extractionId + ".xlsx";
            return new ExcelEntityWriter(filePath);
        }

        @Bean
        @StepScope
        public JpaPagingItemReader<SFCMExtractionEntity> entityReader(
                @Value("#{jobParameters['extractionId']}") String extractionId) {

            JpaPagingItemReader<SFCMExtractionEntity> reader = new JpaPagingItemReader<>();
            reader.setEntityManagerFactory(entityManagerFactory);
            reader.setQueryString("SELECT e FROM SFCMExtractionEntity e WHERE e.extractionId = :extractionId");
            reader.setParameterValues(Map.of("extractionId", new BigInteger(extractionId)));
            return reader;
        }

        @Bean
        public Step excelEntityStep(JpaPagingItemReader<SFCMExtractionEntity> reader, ExcelEntityWriter writer) {
            return new StepBuilder("excelEntityStep", jobRepository)
                    .<SFCMExtractionEntity, SFCMExtractionEntity>chunk(10, transactionManager)
                    .reader(reader)
                    .writer(writer)
                    .build();
        }

        @Bean
        public Job excelEntityJob(Step excelEntityStep) {
            return new JobBuilder("excelEntityJob", jobRepository)
                    .start(excelEntityStep)
                    .build();
        }
===========================


