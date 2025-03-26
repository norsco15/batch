package com.mycompany.extraction.writer;

import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ExecutionContext;
import org.springframework.batch.item.support.AbstractItemStreamItemWriter;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import com.mycompany.extraction.entity.SFCMExtractionSheetEntity;

import lombok.extern.slf4j.Slf4j;

import java.util.Map;

/**
 * Un writer qui écrit dans une sheet d'un Workbook POI,
 * sans utiliser de fichier local. On n'appelle pas workbook.write(...) ici.
 * -> On fait le flush final dans un autre step (UploadXlsToS3Tasklet).
 */
@Slf4j
public class XlsItemWriter extends AbstractItemStreamItemWriter<Map<String, Object>> {

    private final Workbook workbook;
    private final SFCMExtractionSheetEntity sheetEntity;

    public XlsItemWriter(Workbook workbook, SFCMExtractionSheetEntity sheetEntity) {
        this.workbook = workbook;
        this.sheetEntity = sheetEntity;
        setExecutionContextName(this.getClass().getSimpleName());
    }

    @Override
    public void open(ExecutionContext executionContext) {
        super.open(executionContext);
        // rien à faire, on ne crée pas de fichier local
        log.info("[XlsItemWriter] open => sheetName={}", sheetEntity.getSheetName());
    }

    @Override
    public void write(Chunk<? extends Map<String, Object>> chunk) {
        // On obtient ou crée la sheet
        Sheet sheet = workbook.getSheet(sheetEntity.getSheetName());
        if (sheet == null) {
            sheet = workbook.createSheet(sheetEntity.getSheetName());
            createHeaderRow(sheet);
        }

        int rowIndex = sheet.getLastRowNum() + 1;
        for (Map<String, Object> rowData : chunk) {
            Row row = sheet.createRow(rowIndex++);
            writeRow(row, rowData);
        }
    }

    private void createHeaderRow(Sheet sheet) {
        Row headerRow = sheet.createRow(0);
        // Ex. on parcourt SFCMExtractionSheetHeaderEntity
        if (sheetEntity.getExtractionSheetHeaderEntitys() != null) {
            sheetEntity.getExtractionSheetHeaderEntitys().forEach(header -> {
                int colIndex = header.getHeaderOrder().intValue();
                Cell cell = headerRow.createCell(colIndex);
                cell.setCellValue(header.getHeaderName());
            });
        }
    }

    private void writeRow(Row row, Map<String, Object> rowData) {
        // On parcourt SFCMExtractionSheetFieldEntity pour connaître l'ordre des colonnes
        if (sheetEntity.getExtractionSheetFieldEntitys() != null) {
            sheetEntity.getExtractionSheetFieldEntitys().forEach(field -> {
                int colIndex = field.getFieldOrder().intValue();
                Cell cell = row.createCell(colIndex);
                Object value = rowData.get(field.getFieldName().toUpperCase());
                cell.setCellValue(value != null ? value.toString() : "");
            });
        }
    }

    @Override
    public void close() {
        log.info("[XlsItemWriter] close => no file output here, flush is in the final tasklet");
        // On ne fait pas workbook.write(...) ici.
        // Ce sera fait dans le step final (UploadXlsToS3Tasklet).
        super.close();
    }
}
