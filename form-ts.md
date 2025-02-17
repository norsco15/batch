import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatStepperModule } from '@angular/material/stepper';
import { MatIconModule } from '@angular/material/icon';

import { ExtractionService } from '../services/extraction.service';
import {
  JSonExtraction,
  JSonExtractionSQLParameter,
  JSonExtractionSheetHeader,
  JSonExtractionSheetField
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
    MatSelectModule,
    MatCheckboxModule,
    MatStepperModule,
    MatIconModule
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ExtractionFormComponent implements OnInit {

  formAction: 'CREATE' | 'MODIFY' = 'CREATE';

  extraction: JSonExtraction = {
    extractionName: '',
    extractionType: '',
    extractionMail: 'N'
  };

  reportTypes = ['CSV', 'XLS'];

  constructor(
    private router: Router,
    private service: ExtractionService
  ) {}

  ngOnInit(): void {
    // Détecter si on est en mode "update" via l'URL ou autre
    if (this.router.url.includes('/update')) {
      this.formAction = 'MODIFY';
      const st: any = history.state;
      if (st && (st.extractionId || st.extractionName)) {
        // on suppose qu'on a passé l'objet extraction complet en state
        this.extraction = st;
      }
    } else {
      this.formAction = 'CREATE';
    }
    // mail = 'Y' ou 'N'
    if (!this.extraction.extractionMail) {
      this.extraction.extractionMail = 'N';
    }
  }

  /** Step 1: Global => extraName, path, type => CSV/XLS */
  onTypeChange() {
    if (this.extraction.extractionType === 'CSV') {
      // initialiser la structure CSV
      if (!this.extraction.jsonExtractionCSV) {
        this.extraction.jsonExtractionCSV = {
          extpactionCSVSeparator: ';',
          extractionCSVHeader: '',
          extractionDateFormat: '',
          extractionNumberFormat: '',
          jsonExtractionSQL: {
            extractionSQLQuery: '',
            jsonExtractionSQLParameters: []
          }
        };
      }
      // pas de sheet
      this.extraction.jsonExtractionSheet = undefined;
    } else if (this.extraction.extractionType === 'XLS') {
      // reset CSV
      this.extraction.jsonExtractionCSV = undefined;
      if (!this.extraction.jsonExtractionSheet) {
        this.extraction.jsonExtractionSheet = [];
      }
    } else {
      // ni CSV ni XLS
      this.extraction.jsonExtractionCSV = undefined;
      this.extraction.jsonExtractionSheet = undefined;
    }
  }

  /** Step 1: Mail => 'Y' ou 'N' */
  toggleMail(checked: boolean) {
    this.extraction.extractionMail = checked ? 'Y' : 'N';
    if (this.extraction.extractionMail === 'Y') {
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

  // =========== CSV Step ============

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

  // =========== XLS Step ============

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

  addHeader(sheetIndex: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    const sheet = this.extraction.jsonExtractionSheet[sheetIndex];
    if (!sheet.jsonExtractionSheetHeader) {
      sheet.jsonExtractionSheetHeader = [];
    }
    const order = sheet.jsonExtractionSheetHeader.length;
    sheet.jsonExtractionSheetHeader.push({
      headerOrder: order,
      headerName: 'Header' + order,
      // cell style => null
    });
  }

  removeHeader(sheetIndex: number, headerIndex: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    const sheet = this.extraction.jsonExtractionSheet[sheetIndex];
    if (!sheet.jsonExtractionSheetHeader) return;
    sheet.jsonExtractionSheetHeader.splice(headerIndex, 1);
  }

  addField(sheetIndex: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    const sheet = this.extraction.jsonExtractionSheet[sheetIndex];
    if (!sheet.jsonExtractionSheetField) {
      sheet.jsonExtractionSheetField = [];
    }
    const order = sheet.jsonExtractionSheetField.length;
    sheet.jsonExtractionSheetField.push({
      fieldorder: order,
      fieldName: 'Field' + order,
      fieldFormat: ''
    });
  }

  removeField(sheetIndex: number, fieldIndex: number) {
    if (!this.extraction.jsonExtractionSheet) return;
    const sheet = this.extraction.jsonExtractionSheet[sheetIndex];
    if (!sheet.jsonExtractionSheetField) return;
    sheet.jsonExtractionSheetField.splice(fieldIndex, 1);
  }

  // =========== Save / Cancel ===========

  save() {
    if (this.formAction === 'CREATE') {
      this.service.createExtraction(this.extraction).subscribe({
        next: () => this.router.navigate(['/extraction/list']),
        error: (err) => console.error('Create error', err)
      });
    } else {
      this.service.updateExtraction(this.extraction).subscribe({
        next: () => this.router.navigate(['/extraction/list']),
        error: (err) => console.error('Update error', err)
      });
    }
  }

  cancel() {
    this.router.navigate(['/extraction/list']);
  }
}
