modifyForm(data: any) {
    this.form = this.formBuilder.group({
        extractionName: [data?.extractionName || '', Validators.required],
        extractionPath: [data?.extractionPath || '', Validators.required],
        extractionType: [data?.extractionType || 'CSV', Validators.required],
        extractionMail: [data?.extractionMail === 'Y' ? 'Y' : 'N', Validators.required],

        // Mail Settings
        mailSubject: [data?.jsonExtractionMail?.mailSubject || ''],
        mailBody: [data?.jsonExtractionMail?.mailBody || ''],
        mailFrom: [data?.jsonExtractionMail?.mailFrom || ''],
        mailTo: [data?.jsonExtractionMail?.mailTo || ''],
        mailCc: [data?.jsonExtractionMail?.mailCc || ''],
        attachFile: [data?.jsonExtractionMail?.attachFile === 'Y' ? true : false],
        zipFile: [data?.jsonExtractionMail?.zipFile === 'Y' ? true : false],

        // CSV Settings
        csvSettings: this.formBuilder.group({
            separator: [data?.jsonExtractionCSV?.extractionCSVSeparator || ';'],
            header: [data?.jsonExtractionCSV?.extractionCSVHeader || ''],
            dateFormat: [data?.jsonExtractionCSV?.extractionDateFormat || ''],
            numberFormat: [data?.jsonExtractionCSV?.extractionNumberFormat || '']
        }),

        // SQL Settings
        sqlQuery: [data?.jsonExtractionCSV?.jsonExtractionSQL?.extractionSQLQuery || '', Validators.required],
        sqlParameters: this.formBuilder.array(
            data?.jsonExtractionCSV?.jsonExtractionSQL?.jsonExtractionSQLParameter?.map(p =>
                this.formBuilder.group({
                    parameterType: [p.parameterType],
                    parameterName: [p.parameterName],
                    parameterValue: [p.parameterValue]
                })
            ) || []
        ),

        // XLS Settings
        xlsSettings: this.formBuilder.group({
            sheets: this.formBuilder.array(
                data?.jsonExtractionSheet?.map(sheet =>
                    this.formBuilder.group({
                        sheetName: [sheet.sheetName],
                        sheetOrder: [sheet.sheetOrder],
                        headers: this.formBuilder.array(
                            sheet.jsonExtractionSheetHeader?.map(header =>
                                this.formBuilder.group({
                                    headerName: [header.headerName],
                                    headerOrder: [header.headerOrder],
                                    style: this.formBuilder.group({
                                        backgroundColor: [header.jsonExtractionCellStyle?.backgroundColor],
                                        fontColor: [header.jsonExtractionCellStyle?.fontColor],
                                        fontHeight: [header.jsonExtractionCellStyle?.fontHeight],
                                        horizontalAlignment: [header.jsonExtractionCellStyle?.horizontalAlignment]
                                    })
                                })
                            ) || []
                        ),
                        fields: this.formBuilder.array(
                            sheet.jsonExtractionSheetField?.map(field =>
                                this.formBuilder.group({
                                    fieldName: [field.fieldName],
                                    fieldOrder: [field.fieldOrder],
                                    fieldFormat: [field.fieldFormat],
                                    style: this.formBuilder.group({
                                        cellFormat: [field.jsonExtractionCellStyle?.cellFormat],
                                        borderStyle: [field.jsonExtractionCellStyle?.borderStyle],
                                        verticalAlignment: [field.jsonExtractionCellStyle?.verticalAlignment],
                                        fontName: [field.jsonExtractionCellStyle?.fontName]
                                    })
                                })
                            ) || []
                        )
                    })
                ) || []
            )
        })
    });
}