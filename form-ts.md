import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatStepperModule } from '@angular/material/stepper';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { STEPPER_GLOBAL_OPTIONS } from '@angular/cdk/stepper';

import { ExtractionService } from '../services/extraction.service';
import { JSonExtraction } from '../models/extraction.model';
import { ExtractionFormSheetComponent } from './extraction-form-sheet.component';

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
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatCheckboxModule,
    MatStepperModule,
    MatTabsModule,
    MatIconModule,
    ExtractionFormSheetComponent
  ],
  providers: [
    {
      provide: STEPPER_GLOBAL_OPTIONS,
      useValue: { showError: true }
    }
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ExtractionFormComponent implements OnInit {

  formAction: 'CREATE' | 'MODIFY' = 'CREATE';

  extraction: JSonExtraction = {
    extractionId: undefined,
    extractionName: '',
    extractionPath: '',
    extractionType: '',
    extractionMail: false
  };

  reportTypesList = [
    { value: 'CSV', label: 'Delimited File (CSV)' },
    { value: 'XLS', label: 'Excel (XLS)' }
  ];

  constructor(
    private router: Router,
    private service: ExtractionService
  ) { }

  ngOnInit(): void {
    if (this.router.url.includes('/update')) {
      this.formAction = 'MODIFY';
      const st: any = history.state;
      if (st && st.extractionId) {
        this.extraction = st;
      }
    } else {
      this.formAction = 'CREATE';
      this.extraction.extractionName = 'Change me !';
      this.extraction.extractionType = '';
    }
  }

  toggleMail() {
    // extractionMail est un boolean
    if (this.extraction.extractionMail === true) {
      // on init la structure du mail
      if (!this.extraction.jsonExtractionMail) {
        this.extraction.jsonExtractionMail = {
          extractionMailId: undefined,
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
      // on le met à false et on retire jsonExtractionMail
      this.extraction.extractionMail = false;
      this.extraction.jsonExtractionMail = undefined;
    }
  }

  onReportTypeChange() {
    if (this.extraction.extractionType === 'CSV') {
      this.extraction.jsonExtractionCSV = {
        extractionCSVId: undefined,
        extpactionCSVSeparator: ';',
        extractionCSVHeader: '',
        extractionDateFormat: '',
        extractionNumberFormat: '',
        jsonExtractionSQL: {
          extractionSQLId: undefined,
          extractionSQLQuery: ''
        },
        jsonExtractionCSVFormat: {
          extractionCSVFormatId: undefined,
          excludedHeaders: '',
          numberFormat: ''
        }
      };
      this.extraction.jsonExtractionSheet = undefined;
    } else if (this.extraction.extractionType === 'XLS') {
      this.extraction.jsonExtractionSheet = [];
      this.extraction.jsonExtractionSheet.push({
        extractionSheetId: undefined,
        sheetOrder: BigInt(0),
        sheetName: 'Sheet1',
        jsonExtractionSQL: {
          extractionSQLId: undefined,
          extractionSQLQuery: ''
        },
        jsonExtractionSheetHeader: [],
        jsonExtractionSheetField: []
      });
      this.extraction.jsonExtractionCSV = undefined;
    } else {
      // Rien
      this.extraction.jsonExtractionCSV = undefined;
      this.extraction.jsonExtractionSheet = undefined;
    }
  }

  addSheet() {
    if (!this.extraction.jsonExtractionSheet) {
      this.extraction.jsonExtractionSheet = [];
    }
    const idx = BigInt(this.extraction.jsonExtractionSheet.length);
    this.extraction.jsonExtractionSheet.push({
      extractionSheetId: undefined,
      sheetOrder: idx,
      sheetName: 'Sheet' + idx,
      jsonExtractionSQL: {
        extractionSQLId: undefined,
        extractionSQLQuery: ''
      },
      jsonExtractionSheetHeader: [],
      jsonExtractionSheetField: []
    });
  }

  save() {
    if (this.formAction === 'MODIFY') {
      this.service.updateExtraction(this.extraction).subscribe({
        next: (res) => {
          console.log('Extraction updated', res);
          this.router.navigateByUrl('/extraction/list');
        },
        error: (err) => {
          console.error('Error updating extraction', err);
        }
      });
    } else {
      this.service.createExtraction(this.extraction).subscribe({
        next: (res) => {
          console.log('Extraction created', res);
          this.router.navigateByUrl('/extraction/list');
        },
        error: (err) => {
          console.error('Error creating extraction', err);
        }
      });
    }
  }
}
