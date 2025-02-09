package com.example.extraction.mapper;

import com.example.extraction.entity.*;
import com.example.extraction.model.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigInteger;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

class EntityToJSonExtractionMapperTest {

    private EntityToJSonExtractionMapper mapper;

    @BeforeEach
    void setUp() {
        mapper = new EntityToJSonExtractionMapper();
    }

    @Test
    void testMapSCMExtractionEntityToJSonExtraction() {
        // GIVEN : un SFCMExtractionEntity avec quelques champs
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(123));
        entity.setExtractionName("Test Extraction");
        entity.setExtractionType("csv");
        entity.setExtractionMail("test@mail.com");
        entity.setExtractionPath("/tmp/extraction");

        // CSV sub-entity
        SFCMExtractionCSVEntity csvEntity = new SFCMExtractionCSVEntity();
        csvEntity.setExtractionCSVId(BigInteger.valueOf(999));
        csvEntity.setExtractionDateFormat("yyyy-MM-dd");
        entity.setExtractionCSVEntity(csvEntity);

        // Mail sub-entity
        SFCMExtractionMailEntity mailEntity = new SFCMExtractionMailEntity();
        mailEntity.setExtractionMailId(BigInteger.valueOf(1001));
        mailEntity.setMailSubject("Subject");
        mailEntity.setMailBody("Body");
        entity.setExtractionMailEntity(mailEntity);

        // WHEN
        JSonExtraction result = mapper.mapSCMExtractionEntityToJSonExtraction(entity);

        // THEN
        assertNotNull(result);
        assertEquals(BigInteger.valueOf(123), result.getExtractionId());
        assertEquals("Test Extraction", result.getExtractionName());
        assertEquals("csv", result.getExtractionType());
        assertEquals("test@mail.com", result.getExtractionMail());
        assertEquals("/tmp/extraction", result.getExtractionPath());

        // Vérifier la partie CSV
        assertNotNull(result.getJsonExtractionCSV());
        assertEquals(BigInteger.valueOf(999), result.getJsonExtractionCSV().getExtractionCSVId());
        assertEquals("yyyy-MM-dd", result.getJsonExtractionCSV().getExtractionDateFormat());

        // Vérifier la partie Mail
        assertNotNull(result.getJsonExtractionMail());
        assertEquals(BigInteger.valueOf(1001), result.getJsonExtractionMail().getExtractionMailId());
        assertEquals("Subject", result.getJsonExtractionMail().getMailSubject());
        assertEquals("Body", result.getJsonExtractionMail().getMailBody());
    }

    @Test
    void testMapSFCMExtractionMailEntityToJSonExtractionMail() {
        // GIVEN
        SFCMExtractionMailEntity mailEntity = new SFCMExtractionMailEntity();
        mailEntity.setExtractionMailId(BigInteger.valueOf(1));
        mailEntity.setMailSubject("Test subject");
        mailEntity.setMailBody("Test body");
        mailEntity.setMailFrom("from@test.com");
        mailEntity.setMailTo("to@test.com");
        mailEntity.setMailCc("cc@test.com");
        mailEntity.setAttachFile("attach.zip");
        mailEntity.setZipFile("archive.zip");

        // WHEN
        JSonExtractionMail result = mapper.mapSFCMExtractionMailEntityToJSonExtractionMail(mailEntity);

        // THEN
        assertNotNull(result);
        assertEquals(BigInteger.valueOf(1), result.getExtractionMailId());
        assertEquals("Test subject", result.getMailSubject());
        assertEquals("Test body", result.getMailBody());
        assertEquals("from@test.com", result.getMailFrom());
        assertEquals("to@test.com", result.getMailTo());
        assertEquals("cc@test.com", result.getMailCc());
        assertEquals("attach.zip", result.getAttachFile());
        assertEquals("archive.zip", result.getZipFile());
    }

    @Test
    void testMapSFCMExtractionCSVEntityToJSonExtractionCSV() {
        // GIVEN
        SFCMExtractionCSVEntity csvEntity = new SFCMExtractionCSVEntity();
        csvEntity.setExtractionCSVId(BigInteger.valueOf(10));
        csvEntity.setExtractionDateFormat("dd/MM/yyyy");
        csvEntity.setExtractionNumberFormat("#,###.##");
        csvEntity.setExtractionCSVHeader("col1;col2;col3");
        csvEntity.setExtractionCSVSeparator(";");

        // WHEN
        JSonExtractionCSV result = mapper.mapSCMExtractionCSVEntityToJSonExtractionCSV(csvEntity);

        // THEN
        assertNotNull(result);
        assertEquals(BigInteger.valueOf(10), result.getExtractionCSVId());
        assertEquals("dd/MM/yyyy", result.getExtractionDateFormat());
        assertEquals("#,###.##", result.getExtractionNumberFormat());
        assertEquals("col1;col2;col3", result.getExtractionCSVHeader());
        assertEquals(";", result.getExtpactionCSVSeparator());
    }

    @Test
    void testMapSFCMExtractionSheetEntityToJSonExtractionSheet() {
        // GIVEN
        SFCMExtractionSheetEntity sheetEntity = new SFCMExtractionSheetEntity();
        sheetEntity.setExtractionSheetId(BigInteger.valueOf(200));
        sheetEntity.setSheetOrder(BigInteger.valueOf(1));
        sheetEntity.setSheetName("SheetNameTest");

        SFCMExtractionSQLEntity sqlEntity = new SFCMExtractionSQLEntity();
        sqlEntity.setExtractionSQLId(BigInteger.valueOf(300));
        sqlEntity.setExtractionSQLQuery("SELECT * FROM test");
        sheetEntity.setExtractionSQLEntity(sqlEntity);

        // Petit Set de headers
        SFCMExtractionSheetHeaderEntity headerEntity = new SFCMExtractionSheetHeaderEntity();
        headerEntity.setExtractionSheetHeaderId(BigInteger.valueOf(400));
        headerEntity.setHeaderName("HeaderTest");
        headerEntity.setHeaderOrder(BigInteger.valueOf(1));
        headerEntity.setExtractionSheetEntity(sheetEntity);

        sheetEntity.setExtractionSheetHeaderEntitys(Set.of(headerEntity));

        // Petit Set de fields
        SFCMExtractionSheetFieldEntity fieldEntity = new SFCMExtractionSheetFieldEntity();
        fieldEntity.setExtractionSheetFieldId(BigInteger.valueOf(500));
        fieldEntity.setFieldName("FieldTest");
        fieldEntity.setFieldorder(BigInteger.valueOf(1));
        fieldEntity.setExtractionSheetEntity(sheetEntity);

        sheetEntity.setExtractionSheetFieldEntitys(Set.of(fieldEntity));

        // WHEN
        JSonExtractionSheet result = mapper.mapSFCMExtractionSheetEntityToJSonExtractionSheet(sheetEntity);

        // THEN
        assertNotNull(result);
        assertEquals(BigInteger.valueOf(200), result.getExtractionSheetId());
        assertEquals(BigInteger.valueOf(1), result.getSheetOrder());
        assertEquals("SheetNameTest", result.getSheetName());
        
        assertNotNull(result.getJsonExtractionSQL());
        assertEquals(BigInteger.valueOf(300), result.getJsonExtractionSQL().getExtractionSQLId());
        assertEquals("SELECT * FROM test", result.getJsonExtractionSQL().getExtractionSQLQuery());

        // Vérifier les headers
        assertNotNull(result.getJsonExtractionSheetHeader());
        assertEquals(1, result.getJsonExtractionSheetHeader().size());
        JSonExtractionSheetHeader header = result.getJsonExtractionSheetHeader().iterator().next();
        assertEquals(BigInteger.valueOf(400), header.getExtractionSheetHeaderId());
        assertEquals("HeaderTest", header.getHeaderName());

        // Vérifier les fields
        assertNotNull(result.getJsonExtractionSheetField());
        assertEquals(1, result.getJsonExtractionSheetField().size());
        JSonExtractionSheetField field = result.getJsonExtractionSheetField().iterator().next();
        assertEquals(BigInteger.valueOf(500), field.getExtractionSheetFieldId());
        assertEquals("FieldTest", field.getFieldName());
    }

    @Test
    void testMapSFCMExtractionSQLParameterEntityToJSonExtractionSQLParameter() {
        // GIVEN
        SFCMExtractionSQLParameterEntity paramEntity = new SFCMExtractionSQLParameterEntity();
        paramEntity.setExtractionSQLParameterId(BigInteger.valueOf(600));
        paramEntity.setParameterType("String");
        paramEntity.setParameterName("myParam");
        paramEntity.setParameterValue("testValue");

        // WHEN
        JSonExtractionSQLParameter result = mapper.mapSFCMExtractionSQLParameterEntityToJSonExtractionSQLParameter(paramEntity);

        // THEN
        assertNotNull(result);
        assertEquals(BigInteger.valueOf(600), result.getExtractionSQLParameterId());
        assertEquals("String", result.getParametentype());
        assertEquals("myParam", result.getParameterNane());
        assertEquals("testValue", result.getParameterValue());
    }
    
    // Vous pouvez rajouter des tests pour mapSCMExtractionCellStyleEntityToJSonExtractionCellStyle, etc.
}
