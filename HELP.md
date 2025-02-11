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

    /**
     * 1) Test CSV complet :
     * - CSV + CSVFormat + SQL + paramètres SQL + Mail
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_csv_withFormat() {
        // GIVEN
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(BigInteger.valueOf(100));
        json.setExtractionName("CSV Extraction");
        json.setExtractionType("csv");
        json.setExtractionPath("/csv/path");
        json.setExtractionMail("info@csv.com");

        // CSV
        JSonExtractionCSV jsonCSV = new JSonExtractionCSV();
        jsonCSV.setExtractionCSVId(BigInteger.valueOf(10));
        jsonCSV.setExtractionDateFormat("yyyy-MM-dd");
        jsonCSV.setExtractionCSVHeader("col1,col2,col3");
        jsonCSV.setExtpactionCSVSeparator(",");

        // CSV Format
        JSonExtractionCSVFormat csvFormat = new JSonExtractionCSVFormat();
        csvFormat.setExtractionCSVFormatId(BigInteger.valueOf(999));
        csvFormat.setExcludedHeaders("EVENT_ID;LOAN_ID");
        jsonCSV.setJsonExtractionCSVFormat(csvFormat);

        // SQL
        JSonExtractionSQL jsonSql = new JSonExtractionSQL();
        jsonSql.setExtractionSQLId(BigInteger.valueOf(999));
        jsonSql.setExtractionSQLQuery("SELECT * FROM my_table_csv");
        // Paramètres SQL
        JSonExtractionSQLParameter param1 = new JSonExtractionSQLParameter();
        param1.setExtractionSQLParameterId(BigInteger.valueOf(1));
        param1.setParametentype("String");
        param1.setParameterNane("PARAM1");
        param1.setParameterValue("Value1");

        JSonExtractionSQLParameter param2 = new JSonExtractionSQLParameter();
        param2.setExtractionSQLParameterId(BigInteger.valueOf(2));
        param2.setParametentype("Integer");
        param2.setParameterNane("PARAM2");
        param2.setParameterValue("42");

        Set<JSonExtractionSQLParameter> sqlParams = new HashSet<>();
        sqlParams.add(param1);
        sqlParams.add(param2);
        jsonSql.setJsonExtractionSQLParameters(sqlParams);

        jsonCSV.setJsonExtractionSQL(jsonSql);
        json.setJsonExtractionCSV(jsonCSV);

        // Mail
        JSonExtractionMail jsonMail = new JSonExtractionMail();
        jsonMail.setExtractionMailId(BigInteger.valueOf(200));
        jsonMail.setMailSubject("Subject CSV");
        jsonMail.setMailBody("CSV Body");
        jsonMail.setMailFrom("from@test.com");
        json.setJsonExtractionMail(jsonMail);

        // WHEN
        SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

        // THEN
        assertNotNull(entity);
        assertEquals(BigInteger.valueOf(100), entity.getExtractionId());
        assertEquals("CSV Extraction", entity.getExtractionName());
        assertEquals("csv", entity.getExtractionType());
        assertEquals("/csv/path", entity.getExtractionPath());
        assertEquals("info@csv.com", entity.getExtractionMail());

        // CSV
        SFCMExtractionCSVEntity csvEntity = entity.getExtractionCSVEntity();
        assertNotNull(csvEntity);
        assertEquals(BigInteger.valueOf(10), csvEntity.getExtractionCSVId());
        assertEquals("yyyy-MM-dd", csvEntity.getExtractionDateFormat());
        assertEquals("col1,col2,col3", csvEntity.getExtractionCSVHeader());
        assertEquals(",", csvEntity.getExtractionCSVSeparator());

        // CSVFormat
        SFCMExtractionCSVFormatEntity csvFormatEntity = csvEntity.getExtractionCSVFormatEntity();
        assertNotNull(csvFormatEntity);
        assertEquals(BigInteger.valueOf(999), csvFormatEntity.getExtractionCSVFormatId());
        assertEquals("EVENT_ID;LOAN_ID", csvFormatEntity.getExcludedHeaders());

        // SQL
        SFCMExtractionSQLEntity sqlEntity = csvEntity.getExtractionSQLEntity();
        assertNotNull(sqlEntity);
        assertEquals(BigInteger.valueOf(999), sqlEntity.getExtractionSQLId());
        assertEquals("SELECT * FROM my_table_csv", sqlEntity.getExtractionSQLQuery());

        // Paramètres SQL
        Set<SFCMExtractionSQLParameterEntity> paramEntities = sqlEntity.getExtractionSQLParameterEntity();
        assertNotNull(paramEntities);
        assertEquals(2, paramEntities.size());

        // Mail
        SFCMExtractionMailEntity mailEntity = entity.getExtractionMailEntity();
        assertNotNull(mailEntity);
        assertEquals(BigInteger.valueOf(200), mailEntity.getExtractionMailId());
        assertEquals("Subject CSV", mailEntity.getMailSubject());
        assertEquals("CSV Body", mailEntity.getMailBody());
        assertEquals("from@test.com", mailEntity.getMailFrom());
    }

    /**
     * 2) Test XLS :
     * On crée un JSonExtractionSheet avec un header + un field, y compris du cell style.
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_xls_withCellStyle() {
        // GIVEN
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(BigInteger.valueOf(200));
        json.setExtractionName("XLS Extraction");
        json.setExtractionType("xls");

        JSonExtractionSheet sheet = new JSonExtractionSheet();
        sheet.setExtractionSheetId(BigInteger.valueOf(301));
        sheet.setSheetName("Sheet1");

        // SQL du sheet
        JSonExtractionSQL sheetSql = new JSonExtractionSQL();
        sheetSql.setExtractionSQLId(BigInteger.valueOf(999));
        sheetSql.setExtractionSQLQuery("SELECT * FROM xls_table");
        sheet.setJsonExtractionSQL(sheetSql);

        // Header + cell style
        JSonExtractionSheetHeader header = new JSonExtractionSheetHeader();
        header.setExtractionSheetHeaderId(BigInteger.valueOf(401));
        header.setHeaderName("Header1");
        JSonExtractionCellStyle headerStyle = new JSonExtractionCellStyle();
        headerStyle.setExtractionCellStyleId(BigInteger.valueOf(701));
        headerStyle.setCellStyle("BOLD");
        headerStyle.setBackgroundColor("GREEN");
        header.setJsonExtractionCellStyle(headerStyle);

        Set<JSonExtractionSheetHeader> headers = new HashSet<>();
        headers.add(header);
        sheet.setJsonExtractionSheetHeader(headers);

        // Field + cell style
        JSonExtractionSheetField field = new JSonExtractionSheetField();
        field.setExtractionSheetFieldId(BigInteger.valueOf(501));
        field.setFieldName("Field1");
        JSonExtractionCellStyle fieldStyle = new JSonExtractionCellStyle();
        fieldStyle.setExtractionCellStyleId(BigInteger.valueOf(702));
        fieldStyle.setCellStyle("ITALIC");
        field.setJsonExtractionCellStyle(fieldStyle);

        Set<JSonExtractionSheetField> fields = new HashSet<>();
        fields.add(field);
        sheet.setJsonExtractionSheetField(fields);

        // Ajout du sheet dans un set
        Set<JSonExtractionSheet> sheets = new HashSet<>();
        sheets.add(sheet);
        json.setJsonExtractionSheet(sheets);

        // WHEN
        SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

        // THEN
        assertNotNull(entity);
        assertEquals(BigInteger.valueOf(200), entity.getExtractionId());
        assertEquals("XLS Extraction", entity.getExtractionName());
        assertEquals("xls", entity.getExtractionType());

        // Sheets
        Set<SFCMExtractionSheetEntity> sheetEntities = entity.getExtractionSheetEntitys();
        assertNotNull(sheetEntities);
        assertEquals(1, sheetEntities.size());
        SFCMExtractionSheetEntity sheetEntity = sheetEntities.iterator().next();
        assertEquals(BigInteger.valueOf(301), sheetEntity.getExtractionSheetId());
        assertEquals("Sheet1", sheetEntity.getSheetName());

        // SQL
        SFCMExtractionSQLEntity sheetSqlEntity = sheetEntity.getExtractionSQLEntity();
        assertNotNull(sheetSqlEntity);
        assertEquals(BigInteger.valueOf(999), sheetSqlEntity.getExtractionSQLId());
        assertEquals("SELECT * FROM xls_table", sheetSqlEntity.getExtractionSQLQuery());

        // Headers
        Set<SFCMExtractionSheetHeaderEntity> headerEntities = sheetEntity.getExtractionSheetHeaderEntitys();
        assertNotNull(headerEntities);
        assertEquals(1, headerEntities.size());
        SFCMExtractionSheetHeaderEntity h1 = headerEntities.iterator().next();
        assertEquals(BigInteger.valueOf(401), h1.getExtractionSheetHeaderId());
        assertEquals("Header1", h1.getHeaderName());
        // Cell style
        SFCMExtractionCellStyleEntity hStyle = h1.getExtractionCellStyleEntity();
        assertNotNull(hStyle);
        assertEquals(BigInteger.valueOf(701), hStyle.getExtractionCellStyleId());
        assertEquals("BOLD", hStyle.getCellStyle());
        assertEquals("GREEN", hStyle.getBackgroundColor());

        // Fields
        Set<SFCMExtractionSheetFieldEntity> fieldEntities = sheetEntity.getExtractionSheetFieldEntitys();
        assertNotNull(fieldEntities);
        assertEquals(1, fieldEntities.size());
        SFCMExtractionSheetFieldEntity f1 = fieldEntities.iterator().next();
        assertEquals(BigInteger.valueOf(501), f1.getExtractionSheetFieldId());
        assertEquals("Field1", f1.getFieldName());
        // Cell style
        SFCMExtractionCellStyleEntity fStyle = f1.getExtractionCellStyleEntity();
        assertNotNull(fStyle);
        assertEquals(BigInteger.valueOf(702), fStyle.getExtractionCellStyleId());
        assertEquals("ITALIC", fStyle.getCellStyle());
    }

    /**
     * 3) Test CSV sans format :
     * Juste un CSV + pas de CSVFormat, partiel
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_csv_noFormat() {
        // GIVEN
        JSonExtraction json = new JSonExtraction();
        json.setExtractionType("csv");
        JSonExtractionCSV csv = new JSonExtractionCSV();
        csv.setExtractionCSVId(BigInteger.valueOf(10));
        // pas de jsonExtractionCSVFormat
        json.setJsonExtractionCSV(csv);

        // WHEN
        SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

        // THEN
        assertNotNull(entity);
        SFCMExtractionCSVEntity csvEntity = entity.getExtractionCSVEntity();
        assertNotNull(csvEntity);
        assertEquals(BigInteger.valueOf(10), csvEntity.getExtractionCSVId());
        // CSVFormat => null
        assertNull(csvEntity.getExtractionCSVFormatEntity());
    }

    /**
     * 4) Test partiel :
     * Pas de mail, pas de CSV, pas de sheets
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_partial() {
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(BigInteger.valueOf(300));
        json.setExtractionName("Partial Extraction");
        json.setExtractionType("csv"); // juste un type

        SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

        assertNotNull(entity);
        assertEquals(BigInteger.valueOf(300), entity.getExtractionId());
        assertEquals("Partial Extraction", entity.getExtractionName());
        // pas de CSV => null
        assertNull(entity.getExtractionCSVEntity());
        // pas de mail => null
        assertNull(entity.getExtractionMailEntity());
        // pas de sheets => null
        assertNull(entity.getExtractionSheetEntitys());
    }

    /**
     * 5) Test input null => renvoie null
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_null() {
        SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(null);
        assertNull(entity);
    }
}
