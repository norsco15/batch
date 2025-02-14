import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA, ViewChild, ElementRef } from '@angular/core';
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

  // Pour "Import JSON"
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  constructor(
    private router: Router,
    private service: ExtractionService
  ) { }

  ngOnInit(): void {
    const st: any = history.state;
    if (this.router.url.includes('/update') && st && st.extractionId) {
      this.formAction = 'MODIFY';
      this.extraction = st;
      // On peut ajuster si on veut direct initialiser CSV ou XLS 
      // (ex: si extractionType == 'CSV', s'assurer que jsonExtractionCSV n'est pas null, etc.)
    } else if (this.router.url.includes('/create')) {
      this.formAction = 'CREATE';
      // init par défaut
    }
  }

  /** Bouton Cancel => retour à la liste */
  onCancel() {
    this.router.navigateByUrl('/extraction/list');
  }

  /** Import JSON : ouvre un input file */
  onImportJson() {
    this.fileInput.nativeElement.click();
  }

  /** Quand on sélectionne un fichier JSON */
  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e: any) => {
      try {
        const content = JSON.parse(e.target.result);
        // On assigne à extraction
        this.extraction = content;
        // On peut faire un console.log
        console.log('Extraction loaded from JSON:', this.extraction);
      } catch (err) {
        console.error('Invalid JSON file', err);
      }
    };
    reader.readAsText(file);
  }

  toggleMail() {
    if (this.extraction.extractionMail) {
      // on init la structure du mail si pas existant
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
      this.extraction.jsonExtractionMail = undefined;
    }
  }

  onReportTypeChange() {
    if (this.extraction.extractionType === 'CSV') {
      if (!this.extraction.jsonExtractionCSV) {
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
      }
      this.extraction.jsonExtractionSheet = undefined;
    } else if (this.extraction.extractionType === 'XLS') {
      if (!this.extraction.jsonExtractionSheet) {
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
      }
      this.extraction.jsonExtractionCSV = undefined;
    } else {
      // none
      this.extraction.jsonExtractionCSV = undefined;
      this.extraction.jsonExtractionSheet = undefined;
    }
  }

  /** Validation pour stepper : 
   * On désactive "Next" si certains champs sont vides. 
   * Idée simple : on check le stepIndex 
   */
  isStepValid(stepIndex: number): boolean {
    switch (stepIndex) {
      case 0: // Step "Global"
        return !!this.extraction.extractionName && !!this.extraction.extractionType;
      case 1: // Step "Mail" 
        if (this.extraction.extractionMail && this.extraction.jsonExtractionMail) {
          return !!this.extraction.jsonExtractionMail.mailFrom &&
                 !!this.extraction.jsonExtractionMail.mailSubject &&
                 !!this.extraction.jsonExtractionMail.mailTo;
        }
        return true; // si mail pas coché => step ok
      case 2: // Step CSV
        if (this.extraction.extractionType === 'CSV' && this.extraction.jsonExtractionCSV) {
          return !!this.extraction.jsonExtractionCSV.extractionCSVHeader && 
                 !!this.extraction.jsonExtractionCSV.extpactionCSVSeparator;
        }
        return true; // si c'est pas CSV => ok
      case 3: // Step XLS
        if (this.extraction.extractionType === 'XLS' && this.extraction.jsonExtractionSheet) {
          // ex: on vérifie qu'on a au moins un sheetName
          return (this.extraction.jsonExtractionSheet.length > 0 &&
                  !!this.extraction.jsonExtractionSheet[0].sheetName);
        }
        return true; // si pas XLS => ok
      default:
        return true;
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
          this.router.navigateByUrl('/extraction/list');
        },
        error: (err) => console.error('Error updating', err)
      });
    } else {
      this.service.createExtraction(this.extraction).subscribe({
        next: (res) => {
          this.router.navigateByUrl('/extraction/list');
        },
        error: (err) => console.error('Error creating', err)
      });
    }
  }
}
