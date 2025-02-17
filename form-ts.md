import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSelectModule } from '@angular/material/select';
import { MatStepperModule } from '@angular/material/stepper';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';

import { ExtractionService } from '../services/extraction.service';
import { 
  JSonExtraction
} from '../models/extraction.model';

@Component({
  selector: 'app-extraction-form',
  standalone: true,
  templateUrl: './extraction-form.component.html',
  styleUrls: ['./extraction-form.component.css'],
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
    MatSelectModule,
    MatStepperModule,
    MatTabsModule,
    MatIconModule
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ExtractionFormComponent implements OnInit {

  formAction: 'CREATE' | 'MODIFY' = 'CREATE';

  extraction: JSonExtraction = {
    extractionName: '',
    extractionPath: '',
    extractionType: '',
    extractionMail: 'N'
  };

  // Pour afficher la dropdown du type
  reportTypesList = [
    { value: 'CSV', label: 'Delimited File Format (CSV)' },
    { value: 'XLS', label: 'Excel (XLS)' }
  ];

  constructor(
    private router: Router,
    private service: ExtractionService
  ) {}

  ngOnInit(): void {
    // Déterminer si on est en mode CREATE ou MODIFY
    if (this.router.url.includes('/update')) {
      this.formAction = 'MODIFY';
      const st: any = history.state;
      if (st && (st.extractionId || st.extractionName)) {
        // On assigne l'extraction depuis history.state
        this.extraction = st;
      }
    } else {
      this.formAction = 'CREATE';
    }

    // Si extractionMail n'est pas défini, on force 'N'
    if (!this.extraction.extractionMail) {
      this.extraction.extractionMail = 'N';
    }

    // Si on a déjà un extractionType (par ex. CSV/XLS), 
    // on appelle onReportTypeChange pour “déplier” la bonne section
    if (this.extraction.extractionType) {
      this.onReportTypeChange();
    }
  }

  // Step 1: On bascule entre 'Y' / 'N'
  toggleMail() {
    if (this.extraction.extractionMail === 'Y') {
      // On init si besoin
      if (!this.extraction.jsonExtractionMail) {
        this.extraction.jsonExtractionMail = {
          mailSubject: '',
          mailBody: '',
          mailFrom: '',
          mailTo: '',
          mailCc: '',
          attachFile: false,
          zipFile: false
        };
      }
    } else {
      this.extraction.jsonExtractionMail = undefined;
    }
  }

  // Step 1: Quand on change le reportType (CSV / XLS)
  onReportTypeChange() {
    if (this.extraction.extractionType === 'CSV') {
      // Init CSV si pas déjà présent
      if (!this.extraction.jsonExtractionCSV) {
        this.extraction.jsonExtractionCSV = {
          extractionCSVHeader: '',
          extpactionCSVSeparator: ';',
          extractionDateFormat: '',
          extractionNumberFormat: '',
          // CSVFormat (excludedHeaders, numberFormat)
          jsonExtractionCSVFormat: {
            excludedHeaders: '',
            numberFormat: ''
          },
          // SQL
          jsonExtractionSQL: {
            extractionSQLQuery: '',
            jsonExtractionSQLParameters: []
          }
        };
      }
      // On enlève la partie XLS
      this.extraction.jsonExtractionSheet = undefined;

    } else if (this.extraction.extractionType === 'XLS') {
      // On enlève la partie CSV
      this.extraction.jsonExtractionCSV = undefined;
      // On init les sheets si pas déjà
      if (!this.extraction.jsonExtractionSheet) {
        this.extraction.jsonExtractionSheet = [];
      }
    } else {
      // ni CSV ni XLS
      this.extraction.jsonExtractionCSV = undefined;
      this.extraction.jsonExtractionSheet = undefined;
    }
  }

  // Step 3 (CSV) : SQL Params
  addCSVParam() {
    if (!this.extraction.jsonExtractionCSV) return;
    if (!this.extraction.jsonExtractionCSV.jsonExtractionSQL) {
      this.extraction.jsonExtractionCSV.jsonExtractionSQL = {
        extractionSQLQuery: '',
        jsonExtractionSQLParameters: []
      };
    }
    if (!this.extraction.jsonExtractionCSV.jsonExtractionSQL.jsonExtractionSQLParameters) {
      this.extraction.jsonExtractionCSV.jsonExtractionSQL.jsonExtractionSQLParameters = [];
    }
    this.extraction.jsonExtractionCSV.jsonExtractionSQL.jsonExtractionSQLParameters.push({
      parametentype: 'String',
      parameterName: '',
      parameterValue: ''
    });
  }

  removeCSVParam(index: number) {
    if (!this.extraction.jsonExtractionCSV?.jsonExtractionSQL?.jsonExtractionSQLParameters) return;
    this.extraction.jsonExtractionCSV.jsonExtractionSQL.jsonExtractionSQLParameters.splice(index, 1);
  }

  // Step 4 (XLS)

  // Ajouter un sheet
  addSheet() {
    if (!this.extraction.jsonExtractionSheet) {
      this.extraction.jsonExtractionSheet = [];
    }
    const idx = this.extraction.jsonExtractionSheet.length;
    this.extraction.jsonExtractionSheet.push({
      sheetOrder: idx,
      sheetName: 'Sheet' + idx,
      jsonExtractionSQL: {
        extractionSQLQuery: '',
        jsonExtractionSQLParameters: []
      },
      jsonExtractionSheetHeader: [],
      jsonExtractionSheetField: []
    });
  }

  removeSheet(index: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    this.extraction.jsonExtractionSheet.splice(index, 1);
  }

  // Ajouter param XLS
  addXLSParam(sheetIndex: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    const sheet = this.extraction.jsonExtractionSheet[sheetIndex];
    if (!sheet.jsonExtractionSQL) {
      sheet.jsonExtractionSQL = {
        extractionSQLQuery: '',
        jsonExtractionSQLParameters: []
      };
    }
    if (!sheet.jsonExtractionSQL.jsonExtractionSQLParameters) {
      sheet.jsonExtractionSQL.jsonExtractionSQLParameters = [];
    }
    sheet.jsonExtractionSQL.jsonExtractionSQLParameters.push({
      parametentype: 'String',
      parameterName: '',
      parameterValue: ''
    });
  }

  removeXLSParam(sheetIndex: number, paramIndex: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    const sheet = this.extraction.jsonExtractionSheet[sheetIndex];
    if (!sheet.jsonExtractionSQL?.jsonExtractionSQLParameters) return;
    sheet.jsonExtractionSQL.jsonExtractionSQLParameters.splice(paramIndex, 1);
  }

  // Ajouter header
  addHeader(sheetIndex: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    const sheet = this.extraction.jsonExtractionSheet[sheetIndex];
    if (!sheet.jsonExtractionSheetHeader) {
      sheet.jsonExtractionSheetHeader = [];
    }
    const hIndex = sheet.jsonExtractionSheetHeader.length;
    sheet.jsonExtractionSheetHeader.push({
      headerOrder: hIndex,
      headerName: 'Header' + hIndex
    });
  }

  removeHeader(sheetIndex: number, headerIndex: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    const sheet = this.extraction.jsonExtractionSheet[sheetIndex];
    if (!sheet.jsonExtractionSheetHeader) return;
    sheet.jsonExtractionSheetHeader.splice(headerIndex, 1);
  }

  // Ajouter field
  addField(sheetIndex: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    const sheet = this.extraction.jsonExtractionSheet[sheetIndex];
    if (!sheet.jsonExtractionSheetField) {
      sheet.jsonExtractionSheetField = [];
    }
    const fIndex = sheet.jsonExtractionSheetField.length;
    sheet.jsonExtractionSheetField.push({
      fieldOrder: fIndex, // <-- on stocke l'ordre
      fieldName: 'Field' + fIndex,
      fieldFormat: ''
    });
  }

  removeField(sheetIndex: number, fieldIndex: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    const sheet = this.extraction.jsonExtractionSheet[sheetIndex];
    if (!sheet.jsonExtractionSheetField) return;
    sheet.jsonExtractionSheetField.splice(fieldIndex, 1);
  }

  // Step 5: Save
  save() {
    if (this.formAction === 'CREATE') {
      this.service.createExtraction(this.extraction).subscribe({
        next: () => {
          this.router.navigate(['/extraction/list']);
        },
        error: (err) => console.error('Create error', err)
      });
    } else {
      this.service.updateExtraction(this.extraction).subscribe({
        next: () => {
          this.router.navigate(['/extraction/list']);
        },
        error: (err) => console.error('Update error', err)
      });
    }
  }

  cancel() {
    this.router.navigate(['/extraction/list']);
  }
}
