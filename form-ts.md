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
import { JSonExtraction, JSonExtractionCSV, JSonExtractionMail, JSonExtractionSheet } from '../models/extraction.model';
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
    ExtractionFormSheetComponent // on importe le composant "fils"
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
    extractionMail: '',
    jsonExtractionMail: undefined,
    jsonExtractionCSV: undefined,
    jsonExtractionSheet: undefined
  };

  reportTypesList = [
    { value: 'CSV', label: 'Delimited File (CSV)' },
    { value: 'XLS', label: 'Excel (XLS)' }
  ];

  constructor(
    private router: Router,
    private service: ExtractionService
  ) { }

  ngOnInit() {
    if (this.router.url.includes('/update')) {
      this.formAction = 'MODIFY';
      const st: any = history.state;
      if (st && st.extractionId) {
        // On suppose qu'on a déjà l'extraction, sinon on ferait un service.getExtractionById...
        this.extraction = st;
      }
    } else {
      this.formAction = 'CREATE';
      // init par défaut
      this.extraction.extractionName = 'Change me !';
      this.extraction.extractionType = '';
    }
  }

  toggleMail() {
    if (this.extraction.jsonExtractionMail) {
      // on enlève le mail
      this.extraction.jsonExtractionMail = undefined;
    } else {
      // on init le mail
      this.extraction.jsonExtractionMail = {
        extractionMailId: undefined,
        mailSubject: '',
        mailBody: '',
        mailFrom: '',
        mailTo: '',
        mailCc: '',
        attachFile: '',
        zipFile: ''
      };
    }
  }

  onReportTypeChange() {
    // si CSV => on init JSON CSV
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
        }
      };
      this.extraction.jsonExtractionSheet = undefined;
    } else if (this.extraction.extractionType === 'XLS') {
      // XLS => on init la liste de sheets si pas déjà
      this.extraction.jsonExtractionSheet = [];
      // on peut en ajouter 1 par défaut
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
      // ni CSV ni XLS => reset
      this.extraction.jsonExtractionCSV = undefined;
      this.extraction.jsonExtractionSheet = undefined;
    }
  }

  save() {
    if (this.formAction === 'MODIFY') {
      this.service.updateExtraction(this.extraction).subscribe({
        next: (res) => {
          console.log('Extraction updated', res);
          this.router.navigateByUrl('/admin/extraction/list');
        },
        error: (err) => {
          console.error('Error updating', err);
        }
      });
    } else {
      this.service.createExtraction(this.extraction).subscribe({
        next: (res) => {
          console.log('Extraction created', res);
          this.router.navigateByUrl('/admin/extraction/list');
        },
        error: (err) => {
          console.error('Error creating', err);
        }
      });
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
}
