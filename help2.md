package com.example.extraction.mapper;

import com.example.extraction.entity.SFCMExtractionCSVEntity;
import com.example.extraction.entity.SFCMExtractionEntity;
import com.example.extraction.entity.SFCMExtractionMailEntity;
import com.example.extraction.entity.SFCMExtractionSheetEntity;
import com.example.extraction.entity.SFCMExtractionSQLEntity;
import com.example.extraction.model.JSonExtraction;
import com.example.extraction.model.JSonExtractionCSV;
import com.example.extraction.model.JSonExtractionMail;
import com.example.extraction.model.JSonExtractionSheet;
import com.example.extraction.model.JSonExtractionSQL;
import com.example.extraction.model.JSonLaunchExtraction;
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
     * Test de mapping d'un {@link JSonExtraction} en {@link SFCMExtractionEntity}
     * en se concentrant sur le format CSV (jsonExtractionCSV non-null).
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_CsvOnly() {
        // 1) Construire un JSonExtraction avec format CSV
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(BigInteger.valueOf(1));
        json.setExtractionName("My CSV Extraction");
        json.setExtractionType("csv");
        json.setExtractionPath("/csv/path");
        json.setExtractionMail("info@test.com");

        // Sous-objet CSV
        JSonExtractionCSV jsonCSV = new JSonExtractionCSV();
        jsonCSV.setExtractionCSVId(BigInteger.valueOf(10));
        jsonCSV.setExtractionDateFormat("yyyyMMdd");
        jsonCSV.setExtractionCSVHeader("col1,col2,col3");
        jsonCSV.setExtpactionCSVSeparator(",");
        // SQL
        JSonExtractionSQL jsonSql = new JSonExtractionSQL();
        jsonSql.setExtractionSQLId(BigInteger.valueOf(100));
        jsonSql.setExtractionSQLQuery("SELECT * FROM csv_table");
        jsonCSV.setJsonExtractionSQL(jsonSql);

        json.setJsonExtractionCSV(jsonCSV);

        // Sous-objet Mail (facultatif si on veut tester la partie mail aussi)
        JSonExtractionMail jsonMail = new JSonExtractionMail();
        jsonMail.setExtractionMailId(BigInteger.valueOf(20));
        jsonMail.setMailSubject("MailSubject for CSV");
        jsonMail.setMailBody("Body here");
        json.setJsonExtractionMail(jsonMail);

        // Note : on n’ajoute pas de Sheets => c’est un test “focalisé CSV”

        // 2) Appel de la méthode de mapping
        SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

        // 3) Vérifications
        assertNotNull(entity, "L'entité ne doit pas être null");
        assertEquals(BigInteger.valueOf(1), entity.getExtractionId());
        assertEquals("My CSV Extraction", entity.getExtractionName());
        assertEquals("csv", entity.getExtractionType());
        assertEquals("/csv/path", entity.getExtractionPath());
        assertEquals("info@test.com", entity.getExtractionMail());

        // Vérifier CSV
        SFCMExtractionCSVEntity csvEntity = entity.getExtractionCSVEntity();
        assertNotNull(csvEntity, "L'entité CSV ne doit pas être null");
        assertEquals(BigInteger.valueOf(10), csvEntity.getExtractionCSVId());
        assertEquals("yyyyMMdd", csvEntity.getExtractionDateFormat());
        assertEquals("col1,col2,col3", csvEntity.getExtractionCSVHeader());
        assertEquals(",", csvEntity.getExtractionCSVSeparator());

        // Vérifier SQL interne
        SFCMExtractionSQLEntity sqlEntity = csvEntity.getExtractionSQLEntity();
        assertNotNull(sqlEntity, "Le SQL Entity ne doit pas être null");
        assertEquals(BigInteger.valueOf(100), sqlEntity.getExtractionSQLId());
        assertEquals("SELECT * FROM csv_table", sqlEntity.getExtractionSQLQuery());

        // Vérifier Mail
        SFCMExtractionMailEntity mailEntity = entity.getExtractionMailEntity();
        assertNotNull(mailEntity, "Le mail entity ne doit pas être null");
        assertEquals(BigInteger.valueOf(20), mailEntity.getExtractionMailId());
        assertEquals("MailSubject for CSV", mailEntity.getMailSubject());
        assertEquals("Body here", mailEntity.getMailBody());

        // Sheets => null ou vide, selon votre code
        assertTrue(
            entity.getExtractionSheetEntitys() == null ||
            entity.getExtractionSheetEntitys().isEmpty(),
            "Puisqu’on n’a pas fourni de Sheets, ce set doit être null ou vide"
        );
    }

    /**
     * Test de mapping d'un {@link JSonExtraction} partiel (pas de CSV, pas de mail, etc.)
     * pour vérifier qu'on ne plante pas avec des champs null.
     */
    @Test
    void testMapJSonExtractionToSFCMExtractionEntity_NullSubObjects() {
        // 1) JSON partiel
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(BigInteger.valueOf(2));
        json.setExtractionName("Partial JSON");
        json.setExtractionType("csv"); 
        // pas de CSV, pas de mail

        // 2) Appel
        SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

        // 3) Vérifs
        assertNotNull(entity);
        assertEquals(BigInteger.valueOf(2), entity.getExtractionId());
        assertEquals("Partial JSON", entity.getExtractionName());
        assertEquals("csv", entity.getExtractionType());

        // Sous-objets doivent être null
        assertNull(entity.getExtractionCSVEntity());
        assertNull(entity.getExtractionMailEntity());
        assertNull(entity.getExtractionSheetEntitys());
    }
}
