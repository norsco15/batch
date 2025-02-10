package com.example.extraction.mapper;

import com.example.extraction.entity.*;
import com.example.extraction.model.*;
import org.springframework.stereotype.Component;

import java.util.Set;
import java.util.stream.Collectors;

@Component
public class EntityToJSonExtractionMapper {

    public JSonExtraction mapSFCMExtractionEntityToJSonExtraction(SFCMExtractionEntity entity) {
        if (entity == null) {
            return null;
        }
        JSonExtraction json = new JSonExtraction();
        json.setExtractionId(entity.getExtractionId());
        json.setExtractionName(entity.getExtractionName());
        json.setExtractionPath(entity.getExtractionPath());
        json.setExtractionType(entity.getExtractionType());
        json.setExtractionMail(entity.getExtractionMail());

        // Mail
        if (entity.getExtractionMailEntity() != null) {
            json.setJsonExtractionMail(mapSFCMExtractionMailEntityToJSonExtractionMail(entity.getExtractionMailEntity()));
        }

        // CSV
        if (entity.getExtractionCSVEntity() != null) {
            json.setJsonExtractionCSV(mapSFCMExtractionCSVEntityToJSonExtractionCSV(entity.getExtractionCSVEntity()));
        }

        // Sheets
        if (entity.getExtractionSheetEntitys() != null && !entity.getExtractionSheetEntitys().isEmpty()) {
            json.setJsonExtractionSheet(mapSetOfSFCMExtractionSheetEntityToSetOfJSonExtractionSheet(entity.getExtractionSheetEntitys()));
        }

        return json;
    }

    // ---------------------------------------------------------------------------------
    // MAIL
    // ---------------------------------------------------------------------------------
    private JSonExtractionMail mapSFCMExtractionMailEntityToJSonExtractionMail(SFCMExtractionMailEntity entity) {
        if (entity == null) {
            return null;
        }
        JSonExtractionMail json = new JSonExtractionMail();
        json.setExtractionMailId(entity.getExtractionMailId());
        json.setAttachFile(entity.getAttachFile());
        json.setMailBody(entity.getMailBody());
        json.setMailCc(entity.getMailCc());
        json.setMailFrom(entity.getMailFrom());
        json.setMailSubject(entity.getMailSubject());
        json.setMailTo(entity.getMailTo());
        json.setZipFile(entity.getZipFile());
        return json;
    }

    // ---------------------------------------------------------------------------------
    // CSV
    // ---------------------------------------------------------------------------------
    private JSonExtractionCSV mapSFCMExtractionCSVEntityToJSonExtractionCSV(SFCMExtractionCSVEntity entity) {
        if (entity == null) {
            return null;
        }
        JSonExtractionCSV json = new JSonExtractionCSV();
        json.setExtractionCSVId(entity.getExtractionCSVId());
        json.setExtractionCSVHeader(entity.getExtractionCSVHeader());
        json.setExtpactionCSVSeparator(entity.getExtractionCSVSeparator());
        json.setExtractionDateFormat(entity.getExtractionDateFormat());
        json.setExtractionNumberFormat(entity.getExtractionNumberFormat());

        // SQL
        if (entity.getExtractionSQLEntity() != null) {
            json.setJsonExtractionSQL(mapSFCMExtractionSQLEntityToJSonExtractionSQL(entity.getExtractionSQLEntity()));
        }

        return json;
    }

    // ---------------------------------------------------------------------------------
    // SQL
    // ---------------------------------------------------------------------------------
    private JSonExtractionSQL mapSFCMExtractionSQLEntityToJSonExtractionSQL(SFCMExtractionSQLEntity entity) {
        if (entity == null) {
            return null;
        }
        JSonExtractionSQL json = new JSonExtractionSQL();
        json.setExtractionSQLId(entity.getExtractionSQLId());
        json.setExtractionSQLQuery(entity.getExtractionSQLQuery());

        // Paramètres
        if (entity.getExtractionSQLParameterEntity() != null && !entity.getExtractionSQLParameterEntity().isEmpty()) {
            json.setJsonExtractionSQLParameters(
                    mapSetOfSFCMExtractionSQLParameterEntityToSetOfJSonExtractionSQLParameter(entity.getExtractionSQLParameterEntity())
            );
        }

        return json;
    }

    private Set<JSonExtractionSQLParameter> mapSetOfSFCMExtractionSQLParameterEntityToSetOfJSonExtractionSQLParameter(
            Set<SFCMExtractionSQLParameterEntity> entities
    ) {
        return entities.stream()
                .map(this::mapSFCMExtractionSQLParameterEntityToJSonExtractionSQLParameter)
                .collect(Collectors.toSet());
    }

    private JSonExtractionSQLParameter mapSFCMExtractionSQLParameterEntityToJSonExtractionSQLParameter(
            SFCMExtractionSQLParameterEntity entity
    ) {
        if (entity == null) {
            return null;
        }
        JSonExtractionSQLParameter json = new JSonExtractionSQLParameter();
        json.setExtractionSQLParameterId(entity.getExtractionSQLParameterId());
        json.setParametentype(entity.getParameterType());
        json.setParameterNane(entity.getParameterName());
        json.setParameterValue(entity.getParameterValue());
        return json;
    }

    // ---------------------------------------------------------------------------------
    // SHEET
    // ---------------------------------------------------------------------------------
    private Set<JSonExtractionSheet> mapSetOfSFCMExtractionSheetEntityToSetOfJSonExtractionSheet(
            Set<SFCMExtractionSheetEntity> entities
    ) {
        return entities.stream()
                .map(this::mapSFCMExtractionSheetEntityToJSonExtractionSheet)
                .collect(Collectors.toSet());
    }

    private JSonExtractionSheet mapSFCMExtractionSheetEntityToJSonExtractionSheet(SFCMExtractionSheetEntity entity) {
        if (entity == null) {
            return null;
        }
        JSonExtractionSheet json = new JSonExtractionSheet();
        json.setExtractionSheetId(entity.getExtractionSheetId());
        json.setSheetName(entity.getSheetName());
        json.setSheetOrder(entity.getSheetOrder());

        // SQL
        if (entity.getExtractionSQLEntity() != null) {
            json.setJsonExtractionSQL(mapSFCMExtractionSQLEntityToJSonExtractionSQL(entity.getExtractionSQLEntity()));
        }

        // Headers
        if (entity.getExtractionSheetHeaderEntitys() != null && !entity.getExtractionSheetHeaderEntitys().isEmpty()) {
            json.setJsonExtractionSheetHeader(
                    mapSetOfSFCMExtractionSheetHeaderEntityToSetOfJSonExtractionSheetHeader(entity.getExtractionSheetHeaderEntitys())
            );
        }

        // Fields
        if (entity.getExtractionSheetFieldEntitys() != null && !entity.getExtractionSheetFieldEntitys().isEmpty()) {
            json.setJsonExtractionSheetField(
                    mapSetOfSFCMExtractionSheetFieldEntityToSetOfJSonExtractionSheetField(entity.getExtractionSheetFieldEntitys())
            );
        }

        return json;
    }

    private Set<JSonExtractionSheetHeader> mapSetOfSFCMExtractionSheetHeaderEntityToSetOfJSonExtractionSheetHeader(
            Set<SFCMExtractionSheetHeaderEntity> entities
    ) {
        return entities.stream()
                .map(this::mapSFCMExtractionSheetHeaderEntityToJSonExtractionSheetHeader)
                .collect(Collectors.toSet());
    }

    private JSonExtractionSheetHeader mapSFCMExtractionSheetHeaderEntityToJSonExtractionSheetHeader(
            SFCMExtractionSheetHeaderEntity entity
    ) {
        if (entity == null) {
            return null;
        }
        JSonExtractionSheetHeader json = new JSonExtractionSheetHeader();
        json.setExtractionSheetHeaderId(entity.getExtractionSheetHeaderId());
        json.setHeaderName(entity.getHeaderName());
        json.setHeaderOrder(entity.getHeaderOrder());

        // Cell Style
        if (entity.getExtractionCellStyleEntity() != null) {
            json.setJsonExtractionCellStyle(mapSFCMExtractionCellStyleEntityToJSonExtractionCellStyle(entity.getExtractionCellStyleEntity()));
        }

        return json;
    }

    private Set<JSonExtractionSheetField> mapSetOfSFCMExtractionSheetFieldEntityToSetOfJSonExtractionSheetField(
            Set<SFCMExtractionSheetFieldEntity> entities
    ) {
        return entities.stream()
                .map(this::mapSFCMExtractionSheetFieldEntityToJSonExtractionSheetField)
                .collect(Collectors.toSet());
    }

    private JSonExtractionSheetField mapSFCMExtractionSheetFieldEntityToJSonExtractionSheetField(SFCMExtractionSheetFieldEntity entity) {
        if (entity == null) {
            return null;
        }
        JSonExtractionSheetField json = new JSonExtractionSheetField();
        json.setExtractionSheetFieldId(entity.getExtractionSheetFieldId());
        json.setFieldName(entity.getFieldName());
        json.setFieldFormat(entity.getFieldFormat());
        json.setFieldOrder(entity.getFieldOrder());

        // Cell Style
        if (entity.getExtractionCellStyleEntity() != null) {
            json.setJsonExtractionCellStyle(mapSFCMExtractionCellStyleEntityToJSonExtractionCellStyle(entity.getExtractionCellStyleEntity()));
        }

        return json;
    }

    // ---------------------------------------------------------------------------------
    // CELL STYLE
    // ---------------------------------------------------------------------------------
    private JSonExtractionCellStyle mapSFCMExtractionCellStyleEntityToJSonExtractionCellStyle(SFCMExtractionCellStyleEntity entity) {
        if (entity == null) {
            return null;
        }
        JSonExtractionCellStyle json = new JSonExtractionCellStyle();
        json.setExtractionCellStyleId(entity.getExtractionCellStyleId());
        json.setCellStyle(entity.getCellStyle());
        json.setCellFormat(entity.getCellFormat());
        json.setBackgroundColor(entity.getBackgroundColor());
        json.setForegroundColor(entity.getForegroundColor());
        json.setHorizontalAlignment(entity.getHorizontalAlignment());
        json.setVerticalAlignment(entity.getVerticalAlignment());
        json.setBorderStyle(entity.getBorderStyle());
        json.setFontName(entity.getFontName());
        json.setFontColor(entity.getFontColor());
        json.setFontHeight(entity.getFontHeight());
        json.setFontTypographicEmphasis(entity.getFontTypographicEmphasis());
        return json;
    }
}
