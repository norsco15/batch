package com.example.extraction.mapper;

import com.example.extraction.entity.*;
import com.example.extraction.model.*;
import org.springframework.stereotype.Component;

import java.math.BigInteger;
import java.util.HashSet;
import java.util.Set;

@Component
public class JSonToEntityExtractionMapper {

    public SFCMExtractionEntity mapJSonExtractionToSFCMExtractionEntity(JSonExtraction json) {
        if (json == null) {
            return null;
        }
        SFCMExtractionEntity extractionEntity = new SFCMExtractionEntity();

        extractionEntity.setExtractionId(json.getExtractionId());
        extractionEntity.setExtractionName(json.getExtractionName());
        extractionEntity.setExtractionPath(json.getExtractionPath());
        extractionEntity.setExtractionType(json.getExtractionType());
        extractionEntity.setExtractionMail(json.getExtractionMail());

        // Mail
        if (json.getJsonExtractionMail() != null) {
            SFCMExtractionMailEntity mailEntity = mapJsonExtractionMailToExtractionMailEntity(json.getJsonExtractionMail());
            extractionEntity.setExtractionMailEntity(mailEntity);
            mailEntity.setExtractionEntity(extractionEntity);
        }

        // CSV
        if ("csv".equalsIgnoreCase(json.getExtractionType()) && json.getJsonExtractionCSV() != null) {
            SFCMExtractionCSVEntity csvEntity = mapJsonExtractionCSVToExtractionCSVEntity(json.getJsonExtractionCSV());
            extractionEntity.setExtractionCSVEntity(csvEntity);
            csvEntity.setExtractionEntity(extractionEntity);

            JSonExtractionSQL jsonSql = json.getJsonExtractionCSV().getJsonExtractionSQL();
            if (jsonSql != null) {
                SFCMExtractionSQLEntity sqlEntity = mapJsonExtractionSQLToExtractionSQLEntity(jsonSql);
                csvEntity.setExtractionSQLEntity(sqlEntity);
                sqlEntity.setExtractionCSVEntity(csvEntity);

                // Paramètres SQL
                Set<JSonExtractionSQLParameter> jsonParameters = jsonSql.getJsonExtractionSQLParameters();
                if (jsonParameters != null && !jsonParameters.isEmpty()) {
                    Set<SFCMExtractionSQLParameterEntity> sqlParameterEntities = mapSetOfJSonExtractionSQLParameterToSetOfExtractionSQLParameterEntity(jsonParameters, sqlEntity);
                    sqlEntity.setExtractionSQLParameterEntity(sqlParameterEntities);
                }
            }
        }

        // XLS
        if ("xls".equalsIgnoreCase(json.getExtractionType())) {
            if (json.getJsonExtractionSheet() != null && !json.getJsonExtractionSheet().isEmpty()) {
                Set<SFCMExtractionSheetEntity> sheets = mapSetOfJsonExtractionSheetToSetOfExtractionSheetEntity(json.getJsonExtractionSheet(), extractionEntity);
                extractionEntity.setExtractionSheetEntitys(sheets);
            }
        }

        return extractionEntity;
    }

    // ---------------------------------------------------------------------------------
    // MAIL
    // ---------------------------------------------------------------------------------
    private SFCMExtractionMailEntity mapJsonExtractionMailToExtractionMailEntity(JSonExtractionMail json) {
        if (json == null) {
            return null;
        }
        SFCMExtractionMailEntity mailEntity = new SFCMExtractionMailEntity();
        mailEntity.setExtractionMailId(json.getExtractionMailId());
        mailEntity.setAttachFile(json.getAttachFile());
        mailEntity.setMailBody(json.getMailBody());
        mailEntity.setMailCc(json.getMailCc());
        mailEntity.setMailFrom(json.getMailFrom());
        mailEntity.setMailSubject(json.getMailSubject());
        mailEntity.setMailTo(json.getMailTo());
        mailEntity.setZipFile(json.getZipFile());
        return mailEntity;
    }

    // ---------------------------------------------------------------------------------
    // CSV
    // ---------------------------------------------------------------------------------
    private SFCMExtractionCSVEntity mapJsonExtractionCSVToExtractionCSVEntity(JSonExtractionCSV json) {
        if (json == null) {
            return null;
        }
        SFCMExtractionCSVEntity csvEntity = new SFCMExtractionCSVEntity();
        csvEntity.setExtractionCSVId(json.getExtractionCSVId());
        csvEntity.setExtractionCSVHeader(json.getExtractionCSVHeader());
        csvEntity.setExtractionCSVSeparator(json.getExtpactionCSVSeparator());
        csvEntity.setExtractionDateFormat(json.getExtractionDateFormat());
        csvEntity.setExtractionNumberFormat(json.getExtractionNumberFormat());
        return csvEntity;
    }

    // ---------------------------------------------------------------------------------
    // SQL
    // ---------------------------------------------------------------------------------
    private SFCMExtractionSQLEntity mapJsonExtractionSQLToExtractionSQLEntity(JSonExtractionSQL json) {
        if (json == null) {
            return null;
        }
        SFCMExtractionSQLEntity sqlEntity = new SFCMExtractionSQLEntity();
        sqlEntity.setExtractionSQLId(json.getExtractionSQLId());
        sqlEntity.setExtractionSQLQuery(json.getExtractionSQLQuery());
        // Les paramètres SQL seront gérés dans la méthode appelante
        return sqlEntity;
    }

    private SFCMExtractionSQLParameterEntity mapJSonExtractionSQLParameterToExtractionSQLParameterEntity(JSonExtractionSQLParameter json) {
        if (json == null) {
            return null;
        }
        SFCMExtractionSQLParameterEntity sqlParameterEntity = new SFCMExtractionSQLParameterEntity();
        sqlParameterEntity.setExtractionSQLParameterId(json.getExtractionSQLParameterId());
        sqlParameterEntity.setParameterName(json.getParameterName());
        sqlParameterEntity.setParameterType(json.getParametentype());
        sqlParameterEntity.setParameterValue(json.getParameterValue());
        return sqlParameterEntity;
    }

    private Set<SFCMExtractionSQLParameterEntity> mapSetOfJSonExtractionSQLParameterToSetOfExtractionSQLParameterEntity(
            Set<JSonExtractionSQLParameter> jsonParameters,
            SFCMExtractionSQLEntity sqlEntity
    ) {
        Set<SFCMExtractionSQLParameterEntity> sqlParameterEntities = new HashSet<>();
        for (JSonExtractionSQLParameter jsonParam : jsonParameters) {
            SFCMExtractionSQLParameterEntity paramEntity = mapJSonExtractionSQLParameterToExtractionSQLParameterEntity(jsonParam);
            paramEntity.setExtractionSQLEntity(sqlEntity);
            sqlParameterEntities.add(paramEntity);
        }
        return sqlParameterEntities;
    }

    // ---------------------------------------------------------------------------------
    // XLS (Sheets, Headers, Fields, CellStyles)
    // ---------------------------------------------------------------------------------
    private Set<SFCMExtractionSheetEntity> mapSetOfJsonExtractionSheetToSetOfExtractionSheetEntity(
            Set<JSonExtractionSheet> jsonSheets,
            SFCMExtractionEntity extractionEntity
    ) {
        Set<SFCMExtractionSheetEntity> sheets = new HashSet<>();
        for (JSonExtractionSheet jsonSheet : jsonSheets) {
            SFCMExtractionSheetEntity sheetEntity = mapJsonExtractionSheetToExtractionSheetEntity(jsonSheet, extractionEntity);
            sheets.add(sheetEntity);
        }
        return sheets;
    }

    private SFCMExtractionSheetEntity mapJsonExtractionSheetToExtractionSheetEntity(
            JSonExtractionSheet jsonSheet,
            SFCMExtractionEntity extractionEntity
    ) {
        if (jsonSheet == null) {
            return null;
        }
        SFCMExtractionSheetEntity sheetEntity = new SFCMExtractionSheetEntity();
        sheetEntity.setExtractionSheetId(jsonSheet.getExtractionSheetId());
        sheetEntity.setSheetName(jsonSheet.getSheetName());
        sheetEntity.setSheetOrder(jsonSheet.getSheetOrder());
        sheetEntity.setExtractionEntity(extractionEntity);

        // SQL pour le sheet
        if (jsonSheet.getJsonExtractionSQL() != null) {
            SFCMExtractionSQLEntity sqlEntity = mapJsonExtractionSQLToExtractionSQLEntity(jsonSheet.getJsonExtractionSQL());
            sheetEntity.setExtractionSQLEntity(sqlEntity);
            sqlEntity.setExtractionSheetEntity(sheetEntity);

            // Paramètres SQL
            Set<JSonExtractionSQLParameter> jsonSqlParams = jsonSheet.getJsonExtractionSQL().getJsonExtractionSQLParameters();
            if (jsonSqlParams != null && !jsonSqlParams.isEmpty()) {
                Set<SFCMExtractionSQLParameterEntity> sqlParamEntities = mapSetOfJSonExtractionSQLParameterToSetOfExtractionSQLParameterEntity(jsonSqlParams, sqlEntity);
                sqlEntity.setExtractionSQLParameterEntity(sqlParamEntities);
            }
        }

        // Headers
        if (jsonSheet.getJsonExtractionSheetHeader() != null && !jsonSheet.getJsonExtractionSheetHeader().isEmpty()) {
            Set<SFCMExtractionSheetHeaderEntity> sheetHeaders = mapSetOfJsonExtractionSheetHeaderToSetOfExtractionSheetHeaderEntity(
                    jsonSheet.getJsonExtractionSheetHeader(), sheetEntity
            );
            sheetEntity.setExtractionSheetHeaderEntitys(sheetHeaders);
        }

        // Fields
        if (jsonSheet.getJsonExtractionSheetField() != null && !jsonSheet.getJsonExtractionSheetField().isEmpty()) {
            Set<SFCMExtractionSheetFieldEntity> sheetFields = mapSetOfJsonExtractionSheetFieldToSetOfExtractionSheetFieldEntity(
                    jsonSheet.getJsonExtractionSheetField(), sheetEntity
            );
            sheetEntity.setExtractionSheetFieldEntitys(sheetFields);
        }

        return sheetEntity;
    }

    private Set<SFCMExtractionSheetHeaderEntity> mapSetOfJsonExtractionSheetHeaderToSetOfExtractionSheetHeaderEntity(
            Set<JSonExtractionSheetHeader> jsonHeaders,
            SFCMExtractionSheetEntity sheetEntity
    ) {
        Set<SFCMExtractionSheetHeaderEntity> headers = new HashSet<>();
        for (JSonExtractionSheetHeader jsonHeader : jsonHeaders) {
            SFCMExtractionSheetHeaderEntity headerEntity = mapJsonExtractionSheetHeaderToExtractionSheetHeaderEntity(jsonHeader, sheetEntity);
            headers.add(headerEntity);
        }
        return headers;
    }

    private SFCMExtractionSheetHeaderEntity mapJsonExtractionSheetHeaderToExtractionSheetHeaderEntity(
            JSonExtractionSheetHeader jsonSheetHeader,
            SFCMExtractionSheetEntity sheetEntity
    ) {
        if (jsonSheetHeader == null) {
            return null;
        }
        SFCMExtractionSheetHeaderEntity headerEntity = new SFCMExtractionSheetHeaderEntity();
        headerEntity.setExtractionSheetHeaderId(jsonSheetHeader.getExtractionSheetHeaderId());
        headerEntity.setHeaderName(jsonSheetHeader.getHeaderName());
        headerEntity.setHeaderOrder(jsonSheetHeader.getHeaderOrder());
        headerEntity.setExtractionSheetEntity(sheetEntity);

        // Cell Style
        if (jsonSheetHeader.getJsonExtractionCellStyle() != null) {
            SFCMExtractionCellStyleEntity cellStyleEntity = mapJsonExtractionCellStyleToExtractionCellStyleEntity(jsonSheetHeader.getJsonExtractionCellStyle());
            headerEntity.setExtractionCellStyleEntity(cellStyleEntity);
            cellStyleEntity.setExtractionSheetHeaderEntity(headerEntity);
        }

        return headerEntity;
    }

    private Set<SFCMExtractionSheetFieldEntity> mapSetOfJsonExtractionSheetFieldToSetOfExtractionSheetFieldEntity(
            Set<JSonExtractionSheetField> jsonFields,
            SFCMExtractionSheetEntity sheetEntity
    ) {
        Set<SFCMExtractionSheetFieldEntity> fields = new HashSet<>();
        for (JSonExtractionSheetField jsonField : jsonFields) {
            SFCMExtractionSheetFieldEntity fieldEntity = mapJsonExtractionSheetFieldToExtractionSheetFieldEntity(jsonField, sheetEntity);
            fields.add(fieldEntity);
        }
        return fields;
    }

    private SFCMExtractionSheetFieldEntity mapJsonExtractionSheetFieldToExtractionSheetFieldEntity(
            JSonExtractionSheetField jsonSheetField,
            SFCMExtractionSheetEntity sheetEntity
    ) {
        if (jsonSheetField == null) {
            return null;
        }
        SFCMExtractionSheetFieldEntity fieldEntity = new SFCMExtractionSheetFieldEntity();
        fieldEntity.setExtractionSheetFieldId(jsonSheetField.getExtractionSheetFieldId());
        fieldEntity.setFieldOrder(jsonSheetField.getFieldorder());
        fieldEntity.setFieldName(jsonSheetField.getFieldName());
        fieldEntity.setFieldFormat(jsonSheetField.getFieldFormat());
        fieldEntity.setExtractionSheetEntity(sheetEntity);

        // Cell Style
        if (jsonSheetField.getJsonExtractionCellStyle() != null) {
            SFCMExtractionCellStyleEntity cellStyleEntity = mapJsonExtractionCellStyleToExtractionCellStyleEntity(jsonSheetField.getJsonExtractionCellStyle());
            fieldEntity.setExtractionCellStyleEntity(cellStyleEntity);
            cellStyleEntity.setExtractionSheetFieldEntity(fieldEntity);
        }

        return fieldEntity;
    }

    private SFCMExtractionCellStyleEntity mapJsonExtractionCellStyleToExtractionCellStyleEntity(JSonExtractionCellStyle json) {
        if (json == null) {
            return null;
        }
        SFCMExtractionCellStyleEntity cellStyleEntity = new SFCMExtractionCellStyleEntity();
        cellStyleEntity.setExtractionCellStyleId(json.getExtractionCellStyleId());
        cellStyleEntity.setCellStyle(json.getCellStyle());
        cellStyleEntity.setCellFormat(json.getCellFormat());
        cellStyleEntity.setBackgroundColor(json.getBackgroundColor());
        cellStyleEntity.setForegroundColor(json.getForegroundColor());
        cellStyleEntity.setHorizontalAlignment(json.getHorizontalAlignment());
        cellStyleEntity.setVerticalAlignment(json.getVerticalAlignment());
        cellStyleEntity.setBorderStyle(json.getBorderStyle());
        cellStyleEntity.setFontName(json.getFontName());
        cellStyleEntity.setFontColor(json.getFontColor());
        cellStyleEntity.setFontHeight(json.getFontHeight());
        cellStyleEntity.setFontTypographicEmphasis(json.getFontTypographicEmphasis());
        return cellStyleEntity;
    }
}
