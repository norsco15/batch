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
     * Test CSV complet : 
     * On construit un JSonExtraction avec un CSV, un SQL, un mail, 
     * et on vérifie que l'entité SFCMExtractionEntity est correctement peuplée.
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_csv() {
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
        // SQL
        JSonExtractionSQL jsonSql = new JSonExtractionSQL();
        jsonSql.setExtractionSQLId(BigInteger.valueOf(999));
        jsonSql.setExtractionSQLQuery("SELECT * FROM my_table_csv");

        // Paramètres SQL
        JSonExtractionSQLParameter param1 = new JSonExtractionSQLParameter();
        param1.setExtractionSQLParameterId(BigInteger.ONE);
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

        // SQL
        SFCMExtractionSQLEntity sqlEntity = csvEntity.getExtractionSQLEntity();
        assertNotNull(sqlEntity);
        assertEquals(BigInteger.valueOf(999), sqlEntity.getExtractionSQLId());
        assertEquals("SELECT * FROM my_table_csv", sqlEntity.getExtractionSQLQuery());

        // Paramètres SQL
        Set<SFCMExtractionSQLParameterEntity> paramEntities = sqlEntity.getExtractionSQLParameterEntity();
        assertNotNull(paramEntities);
        assertEquals(2, paramEntities.size());
        // On peut les boucler ou simplement vérifier un param
        SFCMExtractionSQLParameterEntity p1 = paramEntities.stream().filter(p -> "PARAM1".equals(p.getParameterName())).findFirst().orElse(null);
        assertNotNull(p1);
        assertEquals("Value1", p1.getParameterValue());

        SFCMExtractionSQLParameterEntity p2 = paramEntities.stream().filter(p -> "PARAM2".equals(p.getParameterName())).findFirst().orElse(null);
        assertNotNull(p2);
        assertEquals("42", p2.getParameterValue());

        // Mail
        SFCMExtractionMailEntity mailEntity = entity.getExtractionMailEntity();
        assertNotNull(mailEntity);
        assertEquals(BigInteger.valueOf(200), mailEntity.getExtractionMailId());
        assertEquals("Subject CSV", mailEntity.getMailSubject());
        assertEquals("CSV Body", mailEntity.getMailBody());
        assertEquals("from@test.com", mailEntity.getMailFrom());

        // Vérifier qu'on n'a pas de Sheets
        assertTrue(entity.getExtractionSheetEntitys() == null || entity.getExtractionSheetEntitys().isEmpty());
    }

    /**
     * Test XLS :
     * On construit un JSonExtraction avec extractionType = "xls", 
     * on ajoute un set de sheets, chacun pouvant avoir son SQL, ses headers, ses fields...
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_xls() {
        // GIVEN
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(BigInteger.valueOf(200));
        json.setExtractionName("XLS Extraction");
        json.setExtractionType("xls");

        // On ajoute un sheet
        JSonExtractionSheet sheet1 = new JSonExtractionSheet();
        sheet1.setExtractionSheetId(BigInteger.valueOf(301));
        sheet1.setSheetName("Sheet1");

        // SQL du sheet
        JSonExtractionSQL sheetSql = new JSonExtractionSQL();
        sheetSql.setExtractionSQLId(BigInteger.valueOf(999));
        sheetSql.setExtractionSQLQuery("SELECT * FROM xls_table");
        sheet1.setJsonExtractionSQL(sheetSql);

        // Headers
        JSonExtractionSheetHeader header = new JSonExtractionSheetHeader();
        header.setExtractionSheetHeaderId(BigInteger.valueOf(401));
        header.setHeaderName("Header1");
        Set<JSonExtractionSheetHeader> headers = new HashSet<>();
        headers.add(header);
        sheet1.setJsonExtractionSheetHeader(headers);

        // Fields
        JSonExtractionSheetField field = new JSonExtractionSheetField();
        field.setExtractionSheetFieldId(BigInteger.valueOf(501));
        field.setFieldName("Field1");
        Set<JSonExtractionSheetField> fields = new HashSet<>();
        fields.add(field);
        sheet1.setJsonExtractionSheetField(fields);

        // On met le sheet dans un set
        Set<JSonExtractionSheet> sheets = new HashSet<>();
        sheets.add(sheet1);
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

        // Fields
        Set<SFCMExtractionSheetFieldEntity> fieldEntities = sheetEntity.getExtractionSheetFieldEntitys();
        assertNotNull(fieldEntities);
        assertEquals(1, fieldEntities.size());
        SFCMExtractionSheetFieldEntity f1 = fieldEntities.iterator().next();
        assertEquals(BigInteger.valueOf(501), f1.getExtractionSheetFieldId());
        assertEquals("Field1", f1.getFieldName());
    }

    /**
     * Test "partiel" : 
     * Pas de mail, pas de CSV, pas de Sheets => On vérifie qu'on ne plante pas, 
     * et que l'entité est partiellement remplie.
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_partial() {
        // GIVEN
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(BigInteger.valueOf(300));
        json.setExtractionName("Partial Extraction");
        json.setExtractionType("csv"); // Just "csv" par ex., mais pas de jsonExtractionCSV

        // WHEN
        SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

        // THEN
        assertNotNull(entity);
        assertEquals(BigInteger.valueOf(300), entity.getExtractionId());
        assertEquals("Partial Extraction", entity.getExtractionName());
        assertEquals("csv", entity.getExtractionType());

        // Pas de CSV => extractionCSVEntity = null
        assertNull(entity.getExtractionCSVEntity());
        // Pas de mail => extractionMailEntity = null
        assertNull(entity.getExtractionMailEntity());
        // Pas de sheets => extractionSheetEntitys = null (ou vide)
        assertTrue(entity.getExtractionSheetEntitys() == null || entity.getExtractionSheetEntitys().isEmpty());
    }

    /**
     * Test du cas null en entrée, 
     * on vérifie que la méthode renvoie null et ne plante pas.
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_nullInput() {
        // WHEN
        SFCMExtractionEntity result = mapper.mapJSonExtractionToSFCMExtractionEntity(null);

        // THEN
        assertNull(result, "Quand l'input est null, on s'attend à null");
    }
}
