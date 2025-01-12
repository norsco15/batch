package com.example.batch.writer;

import com.example.entities.SFCMExtractionSheetEntity;
import com.example.entities.SFCMExtractionSheetFieldEntity;
import com.example.entities.SFCMExtractionSheetHeaderEntity;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.batch.item.file.transform.LineAggregator;
import org.springframework.batch.item.support.AbstractItemStreamItemWriter;

import java.io.FileOutputStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class ExcelSheetWriter extends AbstractItemStreamItemWriter<Map<String, Object>> {

    private final String filePath;
    private final SFCMExtractionSheetEntity sheetEntity;
    private Workbook workbook;

    public ExcelSheetWriter(String filePath, SFCMExtractionSheetEntity sheetEntity) {
        this.filePath = filePath;
        this.sheetEntity = sheetEntity;
    }

    @Override
    public void open(ExecutionContext executionContext) {
        try {
            // Charger le workbook existant ou en créer un nouveau
            workbook = WorkbookFactory.create(new File(filePath));
        } catch (IOException e) {
            workbook = new XSSFWorkbook();
        }
    }

    @Override
    public void write(List<? extends Map<String, Object>> items) throws IOException {
        // Vérifier si la feuille existe, sinon la créer
        Sheet sheet = workbook.getSheet(sheetEntity.getSheetName());
        if (sheet == null) {
            sheet = workbook.createSheet(sheetEntity.getSheetName());
            createHeaderRow(sheet); // Ajouter les headers à la feuille
        }

        // Ajouter les lignes de données
        int rowIndex = sheet.getLastRowNum() + 1;
        for (Map<String, Object> rowData : items) {
            Row row = sheet.createRow(rowIndex++);
            writeRow(row, rowData);
        }
    }

    private void createHeaderRow(Sheet sheet) {
        Row headerRow = sheet.createRow(0);
        Set<SFCMExtractionSheetHeaderEntity> headers = sheetEntity.getExtractionSheetHeaderEntitys();
        int colIndex = 0;
        for (SFCMExtractionSheetHeaderEntity header : headers) {
            Cell cell = headerRow.createCell(colIndex++);
            cell.setCellValue(header.getHeaderName());
            cell.setCellStyle(createHeaderCellStyle());
        }
    }

    private void writeRow(Row row, Map<String, Object> rowData) {
        int colIndex = 0;
        for (Object value : rowData.values()) {
            Cell cell = row.createCell(colIndex++);
            cell.setCellValue(value != null ? value.toString() : "");
            cell.setCellStyle(createDataCellStyle());
        }
    }

    private CellStyle createHeaderCellStyle() {
        CellStyle style = workbook.createCellStyle();
        Font font = workbook.createFont();
        font.setBold(true);
        font.setFontHeightInPoints((short) 12);
        style.setFont(font);
        style.setAlignment(HorizontalAlignment.CENTER);
        style.setVerticalAlignment(VerticalAlignment.CENTER);
        return style;
    }

    private CellStyle createDataCellStyle() {
        CellStyle style = workbook.createCellStyle();
        style.setAlignment(HorizontalAlignment.LEFT);
        style.setVerticalAlignment(VerticalAlignment.CENTER);
        return style;
    }

    @Override
    public void close() {
        try (FileOutputStream fos = new FileOutputStream(filePath)) {
            workbook.write(fos);
            workbook.close();
        } catch (IOException e) {
            throw new RuntimeException("Failed to close Excel file", e);
        }
    }
}
==================

@Configuration
@EnableBatchProcessing
public class BatchConfig {

    private final JobRepository jobRepository;
    private final PlatformTransactionManager transactionManager;
    private final SFCMExtractionRepository extractionRepository;

    public BatchConfig(JobRepository jobRepository, PlatformTransactionManager transactionManager,
                       SFCMExtractionRepository extractionRepository) {
        this.jobRepository = jobRepository;
        this.transactionManager = transactionManager;
        this.extractionRepository = extractionRepository;
    }

    @Bean
    public Job excelJob(List<Step> sheetSteps) {
        JobBuilder jobBuilder = new JobBuilder("excelJob", jobRepository);
        JobFlowBuilder flowBuilder = jobBuilder.start(sheetSteps.get(0));
        for (int i = 1; i < sheetSteps.size(); i++) {
            flowBuilder.next(sheetSteps.get(i));
        }
        return flowBuilder.end().build();
    }

    @Bean
    public List<Step> sheetSteps() {
        List<Step> steps = new ArrayList<>();
        List<SFCMExtractionSheetEntity> sheets = getSheetsFromExtraction();
        for (SFCMExtractionSheetEntity sheet : sheets) {
            steps.add(createStepForSheet(sheet));
        }
        return steps;
    }

    private Step createStepForSheet(SFCMExtractionSheetEntity sheetEntity) {
        return new StepBuilder(sheetEntity.getSheetName(), jobRepository)
                .<Map<String, Object>, Map<String, Object>>chunk(10, transactionManager)
                .reader(jdbcReader(sheetEntity))
                .writer(excelSheetWriter(sheetEntity))
                .build();
    }

    @Bean
    @StepScope
    public JdbcCursorItemReader<Map<String, Object>> jdbcReader(SFCMExtractionSheetEntity sheetEntity) {
        JdbcCursorItemReader<Map<String, Object>> reader = new JdbcCursorItemReader<>();
        reader.setSql(sheetEntity.getExtractionSQLEntity().getExtractionSQLQuery());
        reader.setRowMapper(new DynamicRowMapper());
        return reader;
    }

    @Bean
    @StepScope
    public ExcelSheetWriter excelSheetWriter(SFCMExtractionSheetEntity sheetEntity) {
        String filePath = "output/extraction.xlsx";
        return new ExcelSheetWriter(filePath, sheetEntity);
    }

    private List<SFCMExtractionSheetEntity> getSheetsFromExtraction() {
        SFCMExtractionEntity extraction = extractionRepository.findById(1L) // Exemple d'ID
                .orElseThrow(() -> new RuntimeException("Extraction not found"));
        return new ArrayList<>(extraction.getExtractionSheetEntitys());
    }
}
===============
@PostMapping("/launch-excel/{id}")
public ResponseEntity<String> launchExcelBatch(@PathVariable Long id) {
    try {
        JobParameters jobParameters = new JobParametersBuilder()
                .addLong("extractionId", id)
                .addLong("time", System.currentTimeMillis()) // Pour éviter les collisions
                .toJobParameters();

        jobLauncher.run(excelJob(sheetSteps()), jobParameters);
        return ResponseEntity.ok("Excel batch job launched successfully!");
    } catch (Exception e) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Failed to launch Excel batch job: " + e.getMessage());
    }
}
