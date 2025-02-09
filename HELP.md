package com.example.extraction.mapper;

import com.example.extraction.entity.*;
import com.example.extraction.model.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigInteger;
import java.util.Collections;
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
    void testMapJSonExtractionToSFCMExtractionEntity() {
        // GIVEN
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(BigInteger.valueOf(123));
        json.setExtractionName("TestExtraction");
        json.setExtractionPath("/tmp");
        json.setExtractionType("xls");
        json.setExtractionMail("test@mail.com");

        // CSV
        JSonExtractionCSV jsonCsv = new JSonExtractionCSV();
        jsonCsv.setExtractionCSVId(BigInteger.valueOf(999));
        jsonCsv.setExtractionDateFormat("yyyy-MM-dd");
        json.setJsonExtractionCSV(jsonCsv);

        // Mail
        JSonExtractionMail jsonMail = new JSonExtractionMail();
        jsonMail.setExtractionMailId(BigInteger.valueOf(1001));
        jsonMail.setMailSubject("Subject");
        json.setJsonExtractionMail(jsonMail);

        // WHEN
        SFCMExtractionEntity result = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

        // THEN
        assertNotNull(result);
        assertEquals(BigInteger.valueOf(123), result.getExtractionId());
        assertEquals("TestExtraction", result.getExtractionName());
        assertEquals("/tmp", result.getExtractionPath());
        assertEquals("xls", result.getExtractionType());
        assertEquals("test@mail.com", result.getExtractionMail());

        // Vérifier CSV
        SFCMExtractionCSVEntity csvEntity = result.getExtractionCSVEntity();
        assertNotNull(csvEntity);
        assertEquals(BigInteger.valueOf(999), csvEntity.getExtractionCSVId());
        assertEquals("yyyy-MM-dd", csvEntity.getExtractionDateFormat());

        // Vérifier Mail
        SFCMExtractionMailEntity mailEntity = result.getExtractionMailEntity();
        assertNotNull(mailEntity);
        assertEquals(BigInteger.valueOf(1001), mailEntity.getExtractionMailId());
        assertEquals("Subject", mailEntity.getMailSubject());
    }

    @Test
    void testMapJsonExtractionMailToExtractionMailEntity() {
        // GIVEN
        JSonExtractionMail jsonMail = new JSonExtractionMail();
        jsonMail.setExtractionMailId(BigInteger.valueOf(1));
        jsonMail.setMailSubject("TestSubject");
        jsonMail.setMailBody("TestBody");
        jsonMail.setMailFrom("from@test.com");
        jsonMail.setMailTo("to@test.com");
        jsonMail.setMailCc("cc@test.com");
        jsonMail.setAttachFile("file.zip");
        jsonMail.setZipFile("fileArchive.zip");

        // WHEN
        SFCMExtractionMailEntity result = JSonToEntityExtractionMapper.mapJsonExtractionMailToExtractionMailEntity(jsonMail);

        // THEN
        assertNotNull(result);
        assertEquals(BigInteger.valueOf(1), result.getExtractionMailId());
        assertEquals("TestSubject", result.getMailSubject());
        assertEquals("TestBody", result.getMailBody());
        assertEquals("from@test.com", result.getMailFrom());
        assertEquals("to@test.com", result.getMailTo());
        assertEquals("cc@test.com", result.getMailCc());
        assertEquals("file.zip", result.getAttachFile());
        assertEquals("fileArchive.zip", result.getZipFile());
    }

    @Test
    void testMapJsonExtractionSheetToExtractionSheetEntity() {
        // GIVEN
        JSonExtractionSheet jsonSheet = new JSonExtractionSheet();
        jsonSheet.setExtractionSheetId(BigInteger.valueOf(200));
        jsonSheet.setSheetOrder(BigInteger.ONE);
        jsonSheet.setSheetName("MySheet");

        // SQL
        JSonExtractionSQL jsonSql = new JSonExtractionSQL();
        jsonSql.setExtractionSQLId(BigInteger.valueOf(300));
        jsonSql.setExtractionSQLQuery("SELECT * FROM table");
        jsonSheet.setJsonExtractionSQL(jsonSql);

        // Header
        JSonExtractionSheetHeader header = new JSonExtractionSheetHeader();
        header.setExtractionSheetHeaderId(BigInteger.valueOf(400));
        header.setHeaderName("HeaderTest");
        Set<JSonExtractionSheetHeader> headers = new HashSet<>();
        headers.add(header);
        jsonSheet.setJsonExtractionSheetHeader(headers);

        // Field
        JSonExtractionSheetField field = new JSonExtractionSheetField();
        field.setExtractionSheetFieldId(BigInteger.valueOf(500));
        field.setFieldName("FieldTest");
        Set<JSonExtractionSheetField> fields = new HashSet<>();
        fields.add(field);
        jsonSheet.setJsonExtractionSheetField(fields);

        // WHEN
        SFCMExtractionSheetEntity result = JSonToEntityExtractionMapper.mapJsonExtractionSheetToExtractionSheetEntity(jsonSheet, null);

        // THEN
        assertNotNull(result);
        assertEquals(BigInteger.valueOf(200), result.getExtractionSheetId());
        assertEquals(BigInteger.ONE, result.getSheetOrder());
        assertEquals("MySheet", result.getSheetName());

        // SQL
        SFCMExtractionSQLEntity sqlEntity = result.getExtractionSQLEntity();
        assertNotNull(sqlEntity);
        assertEquals(BigInteger.valueOf(300), sqlEntity.getExtractionSQLId());
        assertEquals("SELECT * FROM table", sqlEntity.getExtractionSQLQuery());

        // Header
        assertNotNull(result.getExtractionSheetHeaderEntitys());
        assertEquals(1, result.getExtractionSheetHeaderEntitys().size());
        SFCMExtractionSheetHeaderEntity headerEntity = result.getExtractionSheetHeaderEntitys().iterator().next();
        assertEquals(BigInteger.valueOf(400), headerEntity.getExtractionSheetHeaderId());
        assertEquals("HeaderTest", headerEntity.getHeaderName());

        // Field
        assertNotNull(result.getExtractionSheetFieldEntitys());
        assertEquals(1, result.getExtractionSheetFieldEntitys().size());
        SFCMExtractionSheetFieldEntity fieldEntity = result.getExtractionSheetFieldEntitys().iterator().next();
        assertEquals(BigInteger.valueOf(500), fieldEntity.getExtractionSheetFieldId());
        assertEquals("FieldTest", fieldEntity.getFieldName());
    }

    // Vous pouvez faire de même pour mapJsonExtractionCSVToExtractionCSVEntity, etc.
}
