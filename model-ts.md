/**
 * Représente l'ensemble des modèles JSON de votre backend
 * Adapté à Angular/TypeScript.
 */

export interface JSonExtraction {
  extractionId?: number;
  extractionName?: string;
  extractionPath?: string;
  extractionType?: string;
  /**
   * extractionMail est désormais un booléen (true/false)
   */
  extractionMail?: boolean;
  
  jsonExtractionMail?: JSonExtractionMail;
  jsonExtractionCSV?: JSonExtractionCSV;
  jsonExtractionSheet?: JSonExtractionSheet[];
}

export interface JSonExtractionMail {
  extractionMailId?: number;
  mailSubject?: string;
  mailBody?: string;
  mailFrom?: string;
  mailTo?: string;
  mailCc?: string;
  attachFile?: boolean | string; 
  zipFile?: boolean | string;
}

export interface JSonExtractionCSV {
  extractionCSVId?: number;
  extpactionCSVSeparator?: string;
  extractionCSVHeader?: string;
  extractionDateFormat?: string;
  extractionNumberFormat?: string;
  jsonExtractionSQL?: JSonExtractionSQL;

  /**
   * Nouveau : CSV Format (excluded headers, number format)
   */
  jsonExtractionCSVFormat?: JSonExtractionCSVFormat;
}

/**
 * Nouvelle table "USR_EXTRACTION_CSV_FORMAT" => entité SFCMExtractionCSVFormatEntity
 */
export interface JSonExtractionCSVFormat {
  extractionCSVFormatId?: number;
  excludedHeaders?: string;  // ex: "EVENT_ID;LOAN_ID"
  numberFormat?: string;     // ex: "#,###.##"
}

export interface JSonExtractionSQL {
  extractionSQLId?: number;
  extractionSQLQuery?: string;
  jsonExtractionSQLParameters?: JSonExtractionSQLParameter[];
}

export interface JSonExtractionSQLParameter {
  extractionSQLParameterId?: number;
  parametentype?: string;  
  parameterName?: string;
  parameterValue?: string;
}

/**
 * XLS structures
 */
export interface JSonExtractionSheet {
  extractionSheetId?: number;
  sheetOrder?: number;
  sheetName?: string;
  jsonExtractionSQL?: JSonExtractionSQL;
  jsonExtractionSheetHeader?: JSonExtractionSheetHeader[];
  jsonExtractionSheetField?: JSonExtractionSheetField[];
}

export interface JSonExtractionSheetHeader {
  extractionSheetHeaderId?: number;
  headerOrder?: number;
  headerName?: string;
  jsonExtractionCellStyle?: JSonExtractionCellStyle;
}

export interface JSonExtractionSheetField {
  extractionSheetFieldId?: number;
  fieldorder?: number;
  fieldName?: string;
  fieldFormat?: string;
  jsonExtractionCellStyle?: JSonExtractionCellStyle;
}

export interface JSonExtractionCellStyle {
  extractionCellStyleId?: number;
  cellStyle?: string;
  cellFormat?: string;
  backgroundColor?: string;
  foregroundColor?: string;
  horizontalAlignment?: string;
  verticalAlignment?: string;
  borderStyle?: string;
  fontName?: string;
  fontColor?: string;
  fontHeight?: number;
  fontTypographicEmphasis?: string;
}

/**
 * Pour lancer une extraction avec des paramètres.
 */
export interface JSonExtractionParameters {
  parameterName?: string;
  parameterValue?: string;
}

/** Contient l'id + liste de paramètres */
export interface JSonLaunchExtraction {
  extractionId: number;
  extractionParameters?: JSonExtractionParameters[];
}
