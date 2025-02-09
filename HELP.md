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
        // Vous pouvez instantier directement si la classe n'a pas besoin d'injections
        mapper = new EntityToJSonExtractionMapper();
    }

    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_Complete() {
        // 1) Construire une entité d’extraction (SFCMExtractionEntity) complète
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(1));
        entity.setExtractionName("Full Extraction");
        entity.setExtractionType("csv");
        entity.setExtractionPath("/tmp");
        entity.setExtractionMail("info@test.com");

        // Sous-objet CSV
        SFCMExtractionCSVEntity csvEntity = new SFCMExtractionCSVEntity();
        csvEntity.setExtractionCSVId(BigInteger.valueOf(10));
        csvEntity.setExtractionDateFormat("yyyy-MM-dd");
        csvEntity.setExtractionCSVHeader("col1;col2;col3");
        entity.setExtractionCSVEntity(csvEntity);

        // Sous-objet Mail
        SFCMExtractionMailEntity mailEntity = new SFCMExtractionMailEntity();
        mailEntity.setExtractionMailId(BigInteger.valueOf(20));
        mailEntity.setMailSubject("MailSubject");
        mailEntity.setMailBody("Hello");
        entity.setExtractionMailEntity(mailEntity);

        // Sous-objet Sheet avec un SQLEntity
        SFCMExtractionSheetEntity sheetEntity = new SFCMExtractionSheetEntity();
        sheetEntity.setExtractionSheetId(BigInteger.valueOf(30));
        sheetEntity.setSheetName("Sheet1");

        // Ajout param SQLEntity
        SFCMExtractionSQLEntity sqlEntity = new SFCMExtractionSQLEntity();
        sqlEntity.setExtractionSQLId(BigInteger.valueOf(40));
        sqlEntity.setExtractionSQLQuery("SELECT * FROM table");
        sheetEntity.setExtractionSQLEntity(sqlEntity);

        // Ajout du sheet dans un set
        Set<SFCMExtractionSheetEntity> sheets = new HashSet<>();
        sheets.add(sheetEntity);
        entity.setExtractionSheetEntitys(sheets);

        // 2) Appel de la méthode publique
        JSonExtraction json = mapper.mapSCMExtractionEntityToJSonExtraction(entity);

        // 3) Vérifications principales
        assertNotNull(json);
        assertEquals(BigInteger.valueOf(1), json.getExtractionId());
        assertEquals("Full Extraction", json.getExtractionName());
        assertEquals("csv", json.getExtractionType());
        assertEquals("/tmp", json.getExtractionPath());
        assertEquals("info@test.com", json.getExtractionMail());

        // Vérifier CSV
        assertNotNull(json.getJsonExtractionCSV());
        assertEquals(BigInteger.valueOf(10), json.getJsonExtractionCSV().getExtractionCSVId());
        assertEquals("yyyy-MM-dd", json.getJsonExtractionCSV().getExtractionDateFormat());
        assertEquals("col1;col2;col3", json.getJsonExtractionCSV().getExtractionCSVHeader());

        // Vérifier Mail
        assertNotNull(json.getJsonExtractionMail());
        assertEquals(BigInteger.valueOf(20), json.getJsonExtractionMail().getExtractionMailId());
        assertEquals("MailSubject", json.getJsonExtractionMail().getMailSubject());
        assertEquals("Hello", json.getJsonExtractionMail().getMailBody());

        // Vérifier Sheets
        assertNotNull(json.getJsonExtractionSheet());
        assertEquals(1, json.getJsonExtractionSheet().size());
        JSonExtractionSheet jsonSheet = json.getJsonExtractionSheet().iterator().next();
        assertEquals(BigInteger.valueOf(30), jsonSheet.getExtractionSheetId());
        assertEquals("Sheet1", jsonSheet.getSheetName());
        // Vérifier SQL
        assertNotNull(jsonSheet.getJsonExtractionSQL());
        assertEquals(BigInteger.valueOf(40), jsonSheet.getJsonExtractionSQL().getExtractionSQLId());
        assertEquals("SELECT * FROM table", jsonSheet.getJsonExtractionSQL().getExtractionSQLQuery());
    }

    @Test
    void testMapSFCMExtractionEntityToJSonExtraction_WithNullSubEntities() {
        // Cas partiel : pas de CSV, pas de Mail, pas de Sheet
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(2));
        entity.setExtractionName("Partial Extraction");
        // Sous-entités null

        JSonExtraction json = mapper.mapSCMExtractionEntityToJSonExtraction(entity);

        assertNotNull(json);
        assertEquals(BigInteger.valueOf(2), json.getExtractionId());
        assertEquals("Partial Extraction", json.getExtractionName());
        // On vérifie que c'est null
        assertNull(json.getJsonExtractionCSV());
        assertNull(json.getJsonExtractionMail());
        // set de sheets doit être null ou vide, selon votre impl
        assertNull(json.getJsonExtractionSheet());
    }
}
