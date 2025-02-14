package com.example.extraction.batch;

import com.example.extraction.entity.SFCMExtractionSheetEntity;
import com.example.extraction.entity.SFCMExtractionSheetFieldEntity;
import com.example.extraction.entity.SFCMExtractionSheetHeaderEntity;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.batch.item.ExecutionContext;
import org.springframework.batch.item.ItemStreamException;
import org.springframework.batch.item.Chunk;

import java.io.File;
import java.io.FileInputStream;
import java.math.BigInteger;
import java.nio.file.Path;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

class XLSItemWriterTest {

    @TempDir
    static Path tempDir; // répertoire temporaire pour nos tests

    private XLSItemWriter writer;
    private SFCMExtractionSheetEntity sheetEntity;
    private File outputDir;
    private String fileName;

    @BeforeEach
    void setUp() {
        // 1) Préparer un SFCMExtractionSheetEntity factice
        sheetEntity = new SFCMExtractionSheetEntity();
        // on simule le name
        sheetEntity.setSheetName("MySheet");

        // HEADERS
        SFCMExtractionSheetHeaderEntity header1 = new SFCMExtractionSheetHeaderEntity();
        header1.setExtractionSheetHeaderId(BigInteger.valueOf(1));
        header1.setHeaderOrder(BigInteger.valueOf(0));
        header1.setHeaderName("ID");

        SFCMExtractionSheetHeaderEntity header2 = new SFCMExtractionSheetHeaderEntity();
        header2.setExtractionSheetHeaderId(BigInteger.valueOf(2));
        header2.setHeaderOrder(BigInteger.valueOf(1));
        header2.setHeaderName("NAME");

        Set<SFCMExtractionSheetHeaderEntity> headers = new HashSet<>();
        headers.add(header1);
        headers.add(header2);
        sheetEntity.setExtractionSheetHeaderEntitys(headers);

        // FIELDS
        SFCMExtractionSheetFieldEntity field1 = new SFCMExtractionSheetFieldEntity();
        field1.setExtractionSheetFieldId(BigInteger.valueOf(11));
        field1.setFieldOrder(BigInteger.valueOf(0));
        field1.setFieldName("ID");

        SFCMExtractionSheetFieldEntity field2 = new SFCMExtractionSheetFieldEntity();
        field2.setExtractionSheetFieldId(BigInteger.valueOf(12));
        field2.setFieldOrder(BigInteger.valueOf(1));
        field2.setFieldName("NAME");

        Set<SFCMExtractionSheetFieldEntity> fields = new HashSet<>();
        fields.add(field1);
        fields.add(field2);
        sheetEntity.setExtractionSheetFieldEntitys(fields);

        // 2) On va instancier XLSItemWriter
        // On override le outputDir via la variable 'tempDir'
        // Dans ton code, c'est "private final String outputDir = "output";"
        // => on peut forcer la main ou on modifie la classe un peu pour l'injection
        // ou on fait un trick : on recopie la classe et modif. 
        // Pour un test rapide, on peut sub-classer XLSItemWriter.

        this.outputDir = tempDir.toFile(); 
        // on prépare un fileName
        this.fileName = outputDir.getAbsolutePath() + "/test.xlsx";

        // On crée une version "custom" de XLSItemWriter
        writer = new XLSItemWriter(sheetEntity) {
            @Override
            public void open(ExecutionContext executionContext) throws ItemStreamException {
                // on modifie juste le fileName pour pointer vers notre temp dir
                this.fileName = XLSItemWriterTest.this.fileName;
                super.open(executionContext);
            }

            @Override
            public void close() throws ItemStreamException {
                super.close();
            }
        };
    }

    @Test
    void testWriteAndClose() throws Exception {
        // 1) Ouvrir
        writer.open(new ExecutionContext());

        // 2) Ecrire un chunk
        Map<String, Object> row1 = new HashMap<>();
        row1.put("ID", 123);
        row1.put("NAME", "Alice");

        Map<String, Object> row2 = new HashMap<>();
        row2.put("ID", 456);
        row2.put("NAME", "Bob");

        Chunk<Map<String, Object>> chunk = new Chunk<>(Arrays.asList(row1, row2));
        writer.write(chunk);

        // 3) Fermer
        writer.close();

        // 4) Vérifier que le fichier Excel est créé
        File resultFile = new File(fileName);
        assertTrue(resultFile.exists(), "Le fichier Excel doit exister");

        // 5) Relire le fichier avec Apache POI pour vérifier le contenu
        try (FileInputStream fis = new FileInputStream(resultFile);
             Workbook wb = new XSSFWorkbook(fis)) {

            Sheet sheet = wb.getSheet("MySheet");
            assertNotNull(sheet, "La feuille doit exister");

            // Vérif des headers
            Row headerRow = sheet.getRow(0);
            assertNotNull(headerRow);
            assertEquals("ID", headerRow.getCell(0).getStringCellValue());
            assertEquals("NAME", headerRow.getCell(1).getStringCellValue());

            // Vérif row1
            Row row1Data = sheet.getRow(1);
            assertNotNull(row1Data);
            assertEquals("123", row1Data.getCell(0).getStringCellValue());
            assertEquals("Alice", row1Data.getCell(1).getStringCellValue());

            // Vérif row2
            Row row2Data = sheet.getRow(2);
            assertNotNull(row2Data);
            assertEquals("456", row2Data.getCell(0).getStringCellValue());
            assertEquals("Bob", row2Data.getCell(1).getStringCellValue());
        }
    }
}
