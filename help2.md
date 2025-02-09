package com.example.extraction.mapper;

import com.example.extraction.entity.*;
import com.example.extraction.model.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigInteger;
import java.util.HashSet;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class JSonToEntityExtractionMapperTest {

    private JSonToEntityExtractionMapper mapper;

    @BeforeEach
    void setUp() {
        mapper = new JSonToEntityExtractionMapper();
    }

    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_Complete() {
        // 1) Construire un JSonExtraction avec sous-objets
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(BigInteger.valueOf(1));
        json.setExtractionName("Full JSON");
        json.setExtractionType("xls");
        json.setExtractionPath("/some/path");
        json.setExtractionMail("info@test.com");

        // CSV
        JSonExtractionCSV jsonCSV = new JSonExtractionCSV();
        jsonCSV.setExtractionCSVId(BigInteger.valueOf(10));
        jsonCSV.setExtractionDateFormat("yyyyMMdd");
        jsonCSV.setExtractionCSVHeader("H1,H2,H3");
        json.setJsonExtractionCSV(jsonCSV);

        // Mail
        JSonExtractionMail jsonMail = new JSonExtractionMail();
        jsonMail.setExtractionMailId(BigInteger.valueOf(20));
        jsonMail.setMailSubject("MailSubject");
        jsonMail.setMailBody("Body here");
        json.setJsonExtractionMail(jsonMail);

        // Sheets
        JSonExtractionSheet sheet = new JSonExtractionSheet();
        sheet.setExtractionSheetId(BigInteger.valueOf(30));
        sheet.setSheetName("Sheet1");
        // SQL
        JSonExtractionSQL sheetSQL = new JSonExtractionSQL();
        sheetSQL.setExtractionSQLId(BigInteger.valueOf(40));
        sheetSQL.setExtractionSQLQuery("SELECT * FROM table");
        sheet.setJsonExtractionSQL(sheetSQL);

        Set<JSonExtractionSheet> sheets = new HashSet<>();
        sheets.add(sheet);
        json.setJsonExtractionSheet(sheets);

        // 2) Appel de la méthode de mapping
        SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

        // 3) Vérifications
        assertNotNull(entity);
        assertEquals(BigInteger.valueOf(1), entity.getExtractionId());
        assertEquals("Full JSON", entity.getExtractionName());
        assertEquals("xls", entity.getExtractionType());
        assertEquals("/some/path", entity.getExtractionPath());
        assertEquals("info@test.com", entity.getExtractionMail());

        // CSV
        SFCMExtractionCSVEntity csvEntity = entity.getExtractionCSVEntity();
        assertNotNull(csvEntity);
        assertEquals(BigInteger.valueOf(10), csvEntity.getExtractionCSVId());
        assertEquals("yyyyMMdd", csvEntity.getExtractionDateFormat());
        assertEquals("H1,H2,H3", csvEntity.getExtractionCSVHeader());

        // Mail
        SFCMExtractionMailEntity mailEntity = entity.getExtractionMailEntity();
        assertNotNull(mailEntity);
        assertEquals(BigInteger.valueOf(20), mailEntity.getExtractionMailId());
        assertEquals("MailSubject", mailEntity.getMailSubject());
        assertEquals("Body here", mailEntity.getMailBody());

        // Sheets
        assertNotNull(entity.getExtractionSheetEntitys());
        assertEquals(1, entity.getExtractionSheetEntitys().size());
        SFCMExtractionSheetEntity sheetEntity = entity.getExtractionSheetEntitys().iterator().next();
        assertEquals(BigInteger.valueOf(30), sheetEntity.getExtractionSheetId());
        assertEquals("Sheet1", sheetEntity.getSheetName());

        // SQL
        SFCMExtractionSQLEntity sqlEntity = sheetEntity.getExtractionSQLEntity();
        assertNotNull(sqlEntity);
        assertEquals(BigInteger.valueOf(40), sqlEntity.getExtractionSQLId());
        assertEquals("SELECT * FROM table", sqlEntity.getExtractionSQLQuery());
    }

    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_NullSubObjects() {
        // 1) JSON partiel
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(BigInteger.valueOf(2));
        json.setExtractionName("Partial JSON");
        // Pas de CSV, pas de mail, pas de sheets

        // 2) Appel
        SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

        // 3) Vérifs
        assertNotNull(entity);
        assertEquals(BigInteger.valueOf(2), entity.getExtractionId());
        assertEquals("Partial JSON", entity.getExtractionName());

        // Sous-objets doivent être null
        assertNull(entity.getExtractionCSVEntity());
        assertNull(entity.getExtractionMailEntity());
        assertNull(entity.getExtractionSheetEntitys()); // ou vide, selon votre code
    }
}
