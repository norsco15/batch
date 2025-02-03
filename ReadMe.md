export class ExtractionFormComponent implements OnInit {
extractionForm: FormGroup;
extractionTypes = ['CSV', 'XLS'];
alignmentOptions = ['LEFT', 'CENTER', 'RIGHT', 'TOP', 'BOTTOM'];
borderStyles = ['NONE', 'THIN', 'MEDIUM', 'THICK', 'DASHED'];
fontEmphases = ['NONE', 'BOLD', 'ITALIC', 'UNDERLINE'];

constructor(private fb: FormBuilder) {}

ngOnInit(): void {
this.initForm();
}

initForm(): void {
this.extractionForm = this.fb.group({
extractionName: ['', Validators.required],
extractionPath: ['', Validators.required],
extractionType: ['CSV', Validators.required],
extractionMail: [''],

      // Mail Section
      mailSubject: [''],
      mailBody: [''],
      mailFrom: ['', Validators.email],
      mailTo: ['', [Validators.required, Validators.email]],
      mailCc: [''],
      attachFile: [false],
      zipFile: [false],
      
      // CSV Section
      csvSettings: this.fb.group({
        separator: [';', [Validators.required, Validators.maxLength(1)]],
        header: [''],
        dateFormat: [''],
        numberFormat: ['']
      }),
      
      // SQL Section
      sqlQuery: ['', Validators.required],
      sqlParameters: this.fb.array([]),
      
      // XLS Section
      xlsSettings: this.fb.group({
        sheets: this.fb.array([])
      })
    });
}

get sqlParameters(): FormArray {
return this.extractionForm.get('sqlParameters') as FormArray;
}

addSqlParameter(): void {
this.sqlParameters.push(this.fb.group({
parameterType: ['', Validators.required],
parameterName: ['', Validators.required],
parameterValue: ['', Validators.required]
}));
}

removeSqlParameter(index: number): void {
this.sqlParameters.removeAt(index);
}

get xlsSheets(): FormArray {
return this.extractionForm.get('xlsSettings.sheets') as FormArray;
}

createXlsSheet(): FormGroup {
return this.fb.group({
sheetName: ['', Validators.required],
sheetOrder: [0, Validators.required],
headers: this.fb.array([]),
fields: this.fb.array([])
});
}

addXlsSheet(): void {
this.xlsSheets.push(this.createXlsSheet());
}

addXlsHeader(sheetIndex: number): void {
const headers = (this.xlsSheets.at(sheetIndex).get('headers') as FormArray);
headers.push(this.fb.group({
headerName: ['', Validators.required],
headerOrder: [0, Validators.required],
style: this.createStyleForm()
}));
}

addXlsField(sheetIndex: number): void {
const fields = (this.xlsSheets.at(sheetIndex).get('fields') as FormArray);
fields.push(this.fb.group({
fieldName: ['', Validators.required],
fieldOrder: [0, Validators.required],
fieldFormat: [''],
style: this.createStyleForm()
}));
}

onSubmit(): void {
if (this.extractionForm.valid) {
const formValue = this.extractionForm.value;
const extraction: Extraction = {
extractionId: null,
extractionName: formValue.extractionName,
extractionPath: formValue.extractionPath,
extractionType: formValue.extractionType,
extractionMail: formValue.extractionMail,
jsonExtractionCSV: this.mapCsvSettings(formValue),
jsonExtractionMail: this.mapMailSettings(formValue),
jsonExtractionSheet: this.mapXlsSettings(formValue)
};

      this.extractionService.save(extraction).subscribe({
        next: (response) => console.log('Success:', response),
        error: (err) => console.error('Error:', err)
      });
    }
}

createStyleForm(): FormGroup {
return this.fb.group({
cellStyle: [''],
cellFormat: [''],
backgroundColor: ['#ffffff'],
foregroundColor: ['#000000'],
horizontalAlignment: ['LEFT'],
verticalAlignment: ['TOP'],
borderStyle: ['NONE'],
fontName: ['Arial'],
fontColor: ['#000000'],
fontHeight: [11, [Validators.min(8), Validators.max(72)]],
fontTypographicEmphasis: ['NONE']
});
}

get showCsvSection(): boolean {
return this.extractionForm.get('extractionType').value === 'CSV';
}

get showXlsSection(): boolean {
return this.extractionForm.get('extractionType').value === 'XLS';
}

private mapCellStyle(style: any): ExtractionCellStyle {
return style ? {
extractionCellStyleId: null,
cellStyle: style.cellStyle,
cellFormat: style.cellFormat,
backgroundColor: style.backgroundColor,
foregroundColor: style.foregroundColor,
horizontalAlignment: style.horizontalAlignment,
verticalAlignment: style.verticalAlignment,
borderStyle: style.borderStyle,
fontName: style.fontName,
fontColor: style.fontColor,
fontHeight: style.fontHeight,
fontTypographicEmphasis: style.fontTypographicEmphasis
} : null;
}

private mapCsvSettings(formValue: any): ExtractionCSV {
if (this.extractionForm.get('extractionType').value !== 'CSV') return null;

    return {
      extractionCSVId: null,
      extractionCSVSeparator: formValue.csvSettings?.separator,
      extractionCSVHeader: formValue.csvSettings?.header,
      extractionDateFormat: formValue.csvSettings?.dateFormat,
      extractionNumberFormat: formValue.csvSettings?.numberFormat,
      jsonExtractionSQL: {
        extractionSQLId: null,
        extractionSQLQuery: formValue.sqlQuery,
        jsonExtractionSQLParameter: formValue.sqlParameters?.map(param => ({
          extractionSQLParameterId: null,
          parameterType: param.parameterType,
          parameterName: param.parameterName,
          parameterValue: param.parameterValue
        }))
      }
    };
}

private mapMailSettings(formValue: any): ExtractionMail {
return {
extractionMailId: null,
mailSubject: formValue.mailSubject,
mailBody: formValue.mailBody,
mailFrom: formValue.mailFrom,
mailTo: formValue.mailTo,
mailCc: formValue.mailCc,
attachFile: formValue.attachFile.toString(),
zipFile: formValue.zipFile.toString()
};
}

private mapXlsSettings(formValue: any): ExtractionSheet[] {
if (this.extractionForm.get('extractionType').value !== 'XLS') return null;

    return formValue.xlsSettings?.sheets?.map(sheet => ({
      extractionSheetId: null,
      sheetorder: sheet.sheetOrder,
      sheetName: sheet.sheetName,
      jsonExtractionSQL: {
        extractionSQLId: null,
        extractionSQLQuery: formValue.sqlQuery,
        jsonExtractionSQLParameter: formValue.sqlParameters?.map(param => ({
          extractionSQLParameterId: null,
          parameterType: param.parameterType,
          parameterName: param.parameterName,
          parameterValue: param.parameterValue
        }))
      },
      jsonExtractionSheetHeader: sheet.headers?.map(header => ({
        extractionSheetHeaderId: null,
        headerorder: header.headerOrder,
        headerName: header.headerName,
        jsonExtractioncellStyle: this.mapCellStyle(header.style)
      })),
      jsonExtractionSheetField: sheet.fields?.map(field => ({
        extractionSheetFieldId: null,
        fieldorder: field.fieldOrder,
        fieldName: field.fieldName,
        fieldFormat: field.fieldFormat,
        jsonExtractioncellStyle: this.mapCellStyle(field.style)
      }))
    }));
}
}