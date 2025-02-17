/**
 * Représente toutes les interfaces envoyées/reçues du backend.
 * extractionMail = 'Y' ou 'N'
 */
export interface JSonExtraction {
  extractionId?: number;
  extractionName?: string;
  extractionPath?: string;
  extractionType?: string;
  extractionMail?: string; // 'Y' ou 'N'

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
  attachFile?: boolean;
  zipFile?: boolean;
}

/** CSV */
export interface JSonExtractionCSV {
  extractionCSVId?: number;
  extpactionCSVSeparator?: string;
  extractionCSVHeader?: string;
  extractionDateFormat?: string;
  extractionNumberFormat?: string;
  jsonExtractionSQL?: JSonExtractionSQL;
}

/** XLS : un ou plusieurs sheets */
export interface JSonExtractionSheet {
  extractionSheetId?: number;
  sheetOrder?: number;
  sheetName?: string;
  jsonExtractionSQL?: JSonExtractionSQL;
  jsonExtractionSheetHeader?: JSonExtractionSheetHeader[];
  jsonExtractionSheetField?: JSonExtractionSheetField[];
}

/** 1 header XLS */
export interface JSonExtractionSheetHeader {
  extractionSheetHeaderId?: number;
  headerOrder?: number;
  headerName?: string;
  // On ignore cellStyle => on envoie toujours null
}

/** 1 field XLS */
export interface JSonExtractionSheetField {
  extractionSheetFieldId?: number;
  fieldorder?: number;
  fieldName?: string;
  fieldFormat?: string;
  // On ignore cellStyle => on envoie toujours null
}

/** Représente un bloc SQL + params */
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

/** Paramètres pour le launch extraction */
export interface JSonLaunchExtraction {
  extractionId: number;
  extractionParameters?: JSonExtractionParameters[];
}

export interface JSonExtractionParameters {
  parameterName?: string;
  parameterValue?: string;
}
