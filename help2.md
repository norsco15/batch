package com.example.extraction.mapper;

import com.example.extraction.entity.*;
import com.example.extraction.model.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigInteger;
import java.util.HashSet;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class EntityToJSonExtractionMapperTest {

    private EntityToJSonExtractionMapper mapper;

    @BeforeEach
    void setUp() {
        mapper = new EntityToJSonExtractionMapper();
    }

    /**
     * Test CSV complet : 
     * L'entité SFCMExtractionEntity contient un CSVEntity + SQL + Mail => 
     * On vérifie que le JSonExtraction final est correctement peuplé.
     */
    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_csv() {
        // GIVEN
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(100));
        entity.setExtractionName("CSV Extraction");
        entity.setExtractionType("csv");
        entity.setExtractionPath("/csv/path");
        entity.setExtractionMail("info@csv.com");

        // CSV
        SFCMExtractionCSVEntity csvEntity = new SFCMExtractionCSVEntity();
        csvEntity.setExtractionCSVId(BigInteger.valueOf(10));
        csvEntity.setExtractionDateFormat("yyyy-MM-dd");
        csvEntity.setExtractionCSVHeader("col1,col2,col3");
        csvEntity.setExtractionCSVSeparator(",");

        // SQL
        SFCMExtractionSQLEntity sqlEntity = new SFCMExtractionSQLEntity();
        sqlEntity.setExtractionSQLId(BigInteger.valueOf(999));
        sqlEntity.setExtractionSQLQuery("SELECT * FROM my_table_csv");
        // Paramètres SQL
        SFCMExtractionSQLParameterEntity p1 = new SFCMExtractionSQLParameterEntity();
        p1.setExtractionSQLParameterId(BigInteger.ONE);
        p1.setParameterName("PARAM1");
        p1.setParameterType("String");
        p1.setParameterValue("Value1");

        SFCMExtractionSQLParameterEntity p2 = new SFCMExtractionSQLParameterEntity();
        p2.setExtractionSQLParameterId(BigInteger.valueOf(2));
        p2.setParameterName("PARAM2");
        p2.setParameterType("Integer");
        p2.setParameterValue("42");

        Set<SFCMExtractionSQLParameterEntity> params = new HashSet<>();
        params.add(p1);
        params.add(p2);
        sqlEntity.setExtractionSQLParameterEntity(params);

        csvEntity.setExtractionSQLEntity(sqlEntity);

        entity.setExtractionCSVEntity(csvEntity);

        // Mail
        SFCMExtractionMailEntity mailEntity = new SFCMExtractionMailEntity();
        mailEntity.setExtractionMailId(BigInteger.valueOf(200));
        mailEntity.setMailSubject("Subject CSV");
        mailEntity.setMailBody("CSV Body");
        mailEntity.setMailFrom("from@test.com");
        entity.setExtractionMailEntity(mailEntity);

        // WHEN
        JSonExtraction json = mapper.mapSFCMExtractionEntityToJSonExtraction(entity);

        // THEN
        assertNotNull(json);
        assertEquals(BigInteger.valueOf(100), json.getExtractionId());
        assertEquals("CSV Extraction", json.getExtractionName());
        assertEquals("csv", json.getExtractionType());
        assertEquals("/csv/path", json.getExtractionPath());
        assertEquals("info@csv.com", json.getExtractionMail());

        // CSV
        JSonExtractionCSV jsonCSV = json.getJsonExtractionCSV();
        assertNotNull(jsonCSV);
        assertEquals(BigInteger.valueOf(10), jsonCSV.getExtractionCSVId());
        assertEquals("yyyy-MM-dd", jsonCSV.getExtractionDateFormat());
        assertEquals("col1,col2,col3", jsonCSV.getExtractionCSVHeader());
        assertEquals(",", jsonCSV.getExtpactionCSVSeparator());

        // SQL
        JSonExtractionSQL jsonSQL = jsonCSV.getJsonExtractionSQL();
        assertNotNull(jsonSQL);
        assertEquals(BigInteger.valueOf(999), jsonSQL.getExtractionSQLId());
        assertEquals("SELECT * FROM my_table_csv", jsonSQL.getExtractionSQLQuery());

        // Paramètres SQL
        Set<JSonExtractionSQLParameter> jsonParams = jsonSQL.getJsonExtractionSQLParameters();
        assertNotNull(jsonParams);
        assertEquals(2, jsonParams.size());
        JSonExtractionSQLParameter jp1 = jsonParams.stream().filter(x -> "PARAM1".equals(x.getParameterNane())).findFirst().orElse(null);
        assertNotNull(jp1);
        assertEquals("Value1", jp1.getParameterValue());

        // Mail
        JSonExtractionMail jsonMail = json.getJsonExtractionMail();
        assertNotNull(jsonMail);
        assertEquals(BigInteger.valueOf(200), jsonMail.getExtractionMailId());
        assertEquals("Subject CSV", jsonMail.getMailSubject());
        assertEquals("CSV Body", jsonMail.getMailBody());
        assertEquals("from@test.com", jsonMail.getMailFrom());

        // On n'a pas de sheets => null ou vide
        assertNull(json.getJsonExtractionSheet(), "Pas de sheet => doit être null");
    }

    /**
     * Test XLS complet (1 sheet, etc.)
     */
    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_xls() {
        // GIVEN
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(200));
        entity.setExtractionName("XLS Extraction");
        entity.setExtractionType("xls");

        // Un sheet
        SFCMExtractionSheetEntity sheet1 = new SFCMExtractionSheetEntity();
        sheet1.setExtractionSheetId(BigInteger.valueOf(300));
        sheet1.setSheetName("Sheet1");

        // SQL
        SFCMExtractionSQLEntity sheetSqlEntity = new SFCMExtractionSQLEntity();
        sheetSqlEntity.setExtractionSQLId(BigInteger.valueOf(999));
        sheetSqlEntity.setExtractionSQLQuery("SELECT * FROM xls_table");
        sheet1.setExtractionSQLEntity(sheetSqlEntity);

        // Headers
        SFCMExtractionSheetHeaderEntity header1 = new SFCMExtractionSheetHeaderEntity();
        header1.setExtractionSheetHeaderId(BigInteger.valueOf(400));
        header1.setHeaderName("Header1");
        Set<SFCMExtractionSheetHeaderEntity> headers = new HashSet<>();
        headers.add(header1);
        sheet1.setExtractionSheetHeaderEntitys(headers);

        // Fields
        SFCMExtractionSheetFieldEntity field1 = new SFCMExtractionSheetFieldEntity();
        field1.setExtractionSheetFieldId(BigInteger.valueOf(500));
        field1.setFieldName("Field1");
        Set<SFCMExtractionSheetFieldEntity> fields = new HashSet<>();
        fields.add(field1);
        sheet1.setExtractionSheetFieldEntitys(fields);

        // Ajout du sheet à l'entité
        Set<SFCMExtractionSheetEntity> sheetEntities = new HashSet<>();
        sheetEntities.add(sheet1);
        entity.setExtractionSheetEntitys(sheetEntities);

        // WHEN
        JSonExtraction json = mapper.mapSFCMExtractionEntityToJSonExtraction(entity);

        // THEN
        assertNotNull(json);
        assertEquals(BigInteger.valueOf(200), json.getExtractionId());
        assertEquals("XLS Extraction", json.getExtractionName());
        assertEquals("xls", json.getExtractionType());

        // Sheets
        assertNotNull(json.getJsonExtractionSheet());
        assertEquals(1, json.getJsonExtractionSheet().size());
        JSonExtractionSheet s1 = json.getJsonExtractionSheet().iterator().next();
        assertEquals(BigInteger.valueOf(300), s1.getExtractionSheetId());
        assertEquals("Sheet1", s1.getSheetName());

        // SQL
        JSonExtractionSQL s1Sql = s1.getJsonExtractionSQL();
        assertNotNull(s1Sql);
        assertEquals(BigInteger.valueOf(999), s1Sql.getExtractionSQLId());
        assertEquals("SELECT * FROM xls_table", s1Sql.getExtractionSQLQuery());

        // Headers
        assertNotNull(s1.getJsonExtractionSheetHeader());
        assertEquals(1, s1.getJsonExtractionSheetHeader().size());
        JSonExtractionSheetHeader h1 = s1.getJsonExtractionSheetHeader().iterator().next();
        assertEquals(BigInteger.valueOf(400), h1.getExtractionSheetHeaderId());
        assertEquals("Header1", h1.getHeaderName());

        // Fields
        assertNotNull(s1.getJsonExtractionSheetField());
        assertEquals(1, s1.getJsonExtractionSheetField().size());
        JSonExtractionSheetField f1 = s1.getJsonExtractionSheetField().iterator().next();
        assertEquals(BigInteger.valueOf(500), f1.getExtractionSheetFieldId());
        assertEquals("Field1", f1.getFieldName());

        // Pas de CSV => null
        assertNull(json.getJsonExtractionCSV());
    }

    /**
     * Test partiel : 
     * Entité sans CSV, sans Sheet => juste un ou deux champs.
     */
    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_partial() {
        // GIVEN
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(300));
        entity.setExtractionName("Partial Entity");
        entity.setExtractionType("csv"); 
        // Pas de CSVEntity, pas de MailEntity, pas de Sheets

        // WHEN
        JSonExtraction json = mapper.mapSFCMExtractionEntityToJSonExtraction(entity);

        // THEN
        assertNotNull(json);
        assertEquals(BigInteger.valueOf(300), json.getExtractionId());
        assertEquals("Partial Entity", json.getExtractionName());
        assertEquals("csv", json.getExtractionType());

        // CSV => null
        assertNull(json.getJsonExtractionCSV());
        // Mail => null
        assertNull(json.getJsonExtractionMail());
        // Sheets => null
        assertNull(json.getJsonExtractionSheet());
    }

    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_nullInput() {
        // WHEN
        JSonExtraction json = mapper.mapSFCMExtractionEntityToJSonExtraction(null);

        // THEN
        assertNull(json, "Quand l'entité est null, on s'attend à null");
    }
}
