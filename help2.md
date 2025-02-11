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
     * 1) Test CSV complet :
     * - CSVEntity + CSVFormatEntity + SQL + params + MailEntity
     */
    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_csv_withFormat() {
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

        // CSVFormat
        SFCMExtractionCSVFormatEntity csvFormatEntity = new SFCMExtractionCSVFormatEntity();
        csvFormatEntity.setExtractionCSVFormatId(BigInteger.valueOf(999));
        csvFormatEntity.setExcludedHeaders("EVENT_ID;LOAN_ID");
        csvEntity.setExtractionCSVFormatEntity(csvFormatEntity);
        csvFormatEntity.setExtractionCSVEntity(csvEntity);

        // SQL
        SFCMExtractionSQLEntity sqlEntity = new SFCMExtractionSQLEntity();
        sqlEntity.setExtractionSQLId(BigInteger.valueOf(999));
        sqlEntity.setExtractionSQLQuery("SELECT * FROM my_table_csv");

        // Params
        SFCMExtractionSQLParameterEntity p1 = new SFCMExtractionSQLParameterEntity();
        p1.setExtractionSQLParameterId(BigInteger.valueOf(1));
        p1.setParameterName("PARAM1");
        p1.setParameterType("String");
        p1.setParameterValue("Value1");

        SFCMExtractionSQLParameterEntity p2 = new SFCMExtractionSQLParameterEntity();
        p2.setExtractionSQLParameterId(BigInteger.valueOf(2));
        p2.setParameterName("PARAM2");
        p2.setParameterType("Integer");
        p2.setParameterValue("42");

        Set<SFCMExtractionSQLParameterEntity> paramSet = new HashSet<>();
        paramSet.add(p1);
        paramSet.add(p2);
        sqlEntity.setExtractionSQLParameterEntity(paramSet);

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

        // CSVFormat
        JSonExtractionCSVFormat jsonCsvFormat = jsonCSV.getJsonExtractionCSVFormat();
        assertNotNull(jsonCsvFormat);
        assertEquals(BigInteger.valueOf(999), jsonCsvFormat.getExtractionCSVFormatId());
        assertEquals("EVENT_ID;LOAN_ID", jsonCsvFormat.getExcludedHeaders());

        // SQL
        JSonExtractionSQL jsonSQL = jsonCSV.getJsonExtractionSQL();
        assertNotNull(jsonSQL);
        assertEquals(BigInteger.valueOf(999), jsonSQL.getExtractionSQLId());
        assertEquals("SELECT * FROM my_table_csv", jsonSQL.getExtractionSQLQuery());

        // Params
        Set<JSonExtractionSQLParameter> jsonParams = jsonSQL.getJsonExtractionSQLParameters();
        assertNotNull(jsonParams);
        assertEquals(2, jsonParams.size());

        // Mail
        JSonExtractionMail jsonMail = json.getJsonExtractionMail();
        assertNotNull(jsonMail);
        assertEquals(BigInteger.valueOf(200), jsonMail.getExtractionMailId());
        assertEquals("Subject CSV", jsonMail.getMailSubject());
        assertEquals("CSV Body", jsonMail.getMailBody());
        assertEquals("from@test.com", jsonMail.getMailFrom());
    }

    /**
     * 2) Test XLS avec sheet, header, field, + cell style
     */
    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_xls_withCellStyle() {
        // GIVEN
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(200));
        entity.setExtractionName("XLS Extraction");
        entity.setExtractionType("xls");

        // sheet
        SFCMExtractionSheetEntity sheetEntity = new SFCMExtractionSheetEntity();
        sheetEntity.setExtractionSheetId(BigInteger.valueOf(301));
        sheetEntity.setSheetName("Sheet1");

        // SQL
        SFCMExtractionSQLEntity sheetSqlEntity = new SFCMExtractionSQLEntity();
        sheetSqlEntity.setExtractionSQLId(BigInteger.valueOf(999));
        sheetSqlEntity.setExtractionSQLQuery("SELECT * FROM xls_table");
        sheetEntity.setExtractionSQLEntity(sheetSqlEntity);

        // Header + cellstyle
        SFCMExtractionSheetHeaderEntity headerEntity = new SFCMExtractionSheetHeaderEntity();
        headerEntity.setExtractionSheetHeaderId(BigInteger.valueOf(401));
        headerEntity.setHeaderName("Header1");
        SFCMExtractionCellStyleEntity headerStyleEntity = new SFCMExtractionCellStyleEntity();
        headerStyleEntity.setExtractionCellStyleId(BigInteger.valueOf(701));
        headerStyleEntity.setCellStyle("BOLD");
        headerStyleEntity.setBackgroundColor("GREEN");
        headerEntity.setExtractionCellStyleEntity(headerStyleEntity);
        headerStyleEntity.setExtractionSheetHeaderEntity(headerEntity);

        Set<SFCMExtractionSheetHeaderEntity> headers = new HashSet<>();
        headers.add(headerEntity);
        sheetEntity.setExtractionSheetHeaderEntitys(headers);

        // Field + cellstyle
        SFCMExtractionSheetFieldEntity fieldEntity = new SFCMExtractionSheetFieldEntity();
        fieldEntity.setExtractionSheetFieldId(BigInteger.valueOf(501));
        fieldEntity.setFieldName("Field1");
        SFCMExtractionCellStyleEntity fieldStyleEntity = new SFCMExtractionCellStyleEntity();
        fieldStyleEntity.setExtractionCellStyleId(BigInteger.valueOf(702));
        fieldStyleEntity.setCellStyle("ITALIC");
        fieldEntity.setExtractionCellStyleEntity(fieldStyleEntity);
        fieldStyleEntity.setExtractionSheetFieldEntity(fieldEntity);

        Set<SFCMExtractionSheetFieldEntity> fields = new HashSet<>();
        fields.add(fieldEntity);
        sheetEntity.setExtractionSheetFieldEntitys(fields);

        Set<SFCMExtractionSheetEntity> sheetEntities = new HashSet<>();
        sheetEntities.add(sheetEntity);
        entity.setExtractionSheetEntitys(sheetEntities);

        // WHEN
        JSonExtraction json = mapper.mapSFCMExtractionEntityToJSonExtraction(entity);

        // THEN
        assertNotNull(json);
        assertEquals(BigInteger.valueOf(200), json.getExtractionId());
        assertEquals("XLS Extraction", json.getExtractionName());
        assertEquals("xls", json.getExtractionType());

        // Sheet
        Set<JSonExtractionSheet> jsonSheets = json.getJsonExtractionSheet();
        assertNotNull(jsonSheets);
        assertEquals(1, jsonSheets.size());
        JSonExtractionSheet s1 = jsonSheets.iterator().next();
        assertEquals(BigInteger.valueOf(301), s1.getExtractionSheetId());
        assertEquals("Sheet1", s1.getSheetName());

        // SQL
        JSonExtractionSQL s1Sql = s1.getJsonExtractionSQL();
        assertNotNull(s1Sql);
        assertEquals(BigInteger.valueOf(999), s1Sql.getExtractionSQLId());
        assertEquals("SELECT * FROM xls_table", s1Sql.getExtractionSQLQuery());

        // Header + style
        Set<JSonExtractionSheetHeader> jHeaders = s1.getJsonExtractionSheetHeader();
        assertNotNull(jHeaders);
        assertEquals(1, jHeaders.size());
        JSonExtractionSheetHeader h1 = jHeaders.iterator().next();
        assertEquals(BigInteger.valueOf(401), h1.getExtractionSheetHeaderId());
        assertEquals("Header1", h1.getHeaderName());
        JSonExtractionCellStyle hStyle = h1.getJsonExtractionCellStyle();
        assertNotNull(hStyle);
        assertEquals(BigInteger.valueOf(701), hStyle.getExtractionCellStyleId());
        assertEquals("BOLD", hStyle.getCellStyle());
        assertEquals("GREEN", hStyle.getBackgroundColor());

        // Field + style
        Set<JSonExtractionSheetField> jFields = s1.getJsonExtractionSheetField();
        assertNotNull(jFields);
        assertEquals(1, jFields.size());
        JSonExtractionSheetField f1 = jFields.iterator().next();
        assertEquals(BigInteger.valueOf(501), f1.getExtractionSheetFieldId());
        assertEquals("Field1", f1.getFieldName());
        JSonExtractionCellStyle fStyle = f1.getJsonExtractionCellStyle();
        assertNotNull(fStyle);
        assertEquals(BigInteger.valueOf(702), fStyle.getExtractionCellStyleId());
        assertEquals("ITALIC", fStyle.getCellStyle());
    }

    /**
     * 3) Test CSV sans format
     */
    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_csv_noFormat() {
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionType("csv");
        SFCMExtractionCSVEntity csvEntity = new SFCMExtractionCSVEntity();
        csvEntity.setExtractionCSVId(BigInteger.valueOf(10));
        // pas de extractionCSVFormatEntity
        entity.setExtractionCSVEntity(csvEntity);

        JSonExtraction json = mapper.mapSFCMExtractionEntityToJSonExtraction(entity);

        assertNotNull(json.getJsonExtractionCSV());
        assertEquals(BigInteger.valueOf(10), json.getJsonExtractionCSV().getExtractionCSVId());
        // CSVFormat => null
        assertNull(json.getJsonExtractionCSV().getJsonExtractionCSVFormat());
    }

    /**
     * 4) Test partiel :
     * Pas de mail, pas de CSV, pas de sheets
     */
    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_partial() {
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(300));
        entity.setExtractionName("Partial Entity");
        entity.setExtractionType("csv"); 

        JSonExtraction json = mapper.mapSFCMExtractionEntityToJSonExtraction(entity);

        assertNotNull(json);
        assertEquals(BigInteger.valueOf(300), json.getExtractionId());
        assertEquals("Partial Entity", json.getExtractionName());
        assertEquals("csv", json.getExtractionType());

        // CSV => null
        assertNull(json.getJsonExtractionCSV());
        // mail => null
        assertNull(json.getJsonExtractionMail());
        // sheet => null
        assertNull(json.getJsonExtractionSheet());
    }

    /**
     * 5) Test input null => renvoie null
     */
    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_null() {
        JSonExtraction json = mapper.mapSFCMExtractionEntityToJSonExtraction(null);
        assertNull(json);
    }
}
