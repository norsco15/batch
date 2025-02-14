<mat-card>
  <mat-card-header>
    <mat-card-title>
      {{ formAction === 'CREATE' ? 'Create Extraction' : 'Update Extraction' }}
    </mat-card-title>
  </mat-card-header>

  <mat-card-content>
    <!-- Bouton Import -->
    <button mat-raised-button color="accent" (click)="onImportJson()">Import JSON</button>
    <input #fileInput type="file" (change)="onFileSelected($event)" accept=".json" hidden />

    <mat-stepper #stepper orientation="horizontal">

      <mat-step label="Global" [completed]="isStepValid(0)" [optional]="false">
        <input type="hidden" [(ngModel)]="extraction.extractionId" />

        <mat-form-field class="mr-sm-2">
          <mat-label>Report Name</mat-label>
          <input matInput required [(ngModel)]="extraction.extractionName">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>File Path</mat-label>
          <input matInput [(ngModel)]="extraction.extractionPath">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Report Type</mat-label>
          <mat-select required [(ngModel)]="extraction.extractionType" (selectionChange)="onReportTypeChange()">
            <mat-option *ngFor="let rt of reportTypesList" [value]="rt.value">
              {{ rt.label }}
            </mat-option>
          </mat-select>
        </mat-form-field>
        <br />

        <mat-checkbox [(ngModel)]="extraction.extractionMail" (change)="toggleMail()">
          Send Mail ?
        </mat-checkbox>
        <br />

        <div>
          <button mat-button matStepperNext [disabled]="!isStepValid(0)">Next</button>
        </div>
      </mat-step>

      <mat-step label="Mail" [completed]="isStepValid(1)" *ngIf="extraction.extractionMail" [optional]="false">
        <mat-form-field class="mr-sm-2">
          <mat-label>From</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailFrom" required>
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Subject</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailSubject" required>
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>To</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailTo" required>
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>CC</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailCc">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Mail Body</mat-label>
          <textarea matInput rows="3" [(ngModel)]="extraction.jsonExtractionMail?.mailBody"></textarea>
        </mat-form-field>
        <br />

        <mat-checkbox [(ngModel)]="extraction.jsonExtractionMail?.attachFile">Attach File?</mat-checkbox>
        <mat-checkbox [(ngModel)]="extraction.jsonExtractionMail?.zipFile">Zip File?</mat-checkbox>
        <br />

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext [disabled]="!isStepValid(1)">Next</button>
        </div>
      </mat-step>

      <mat-step label="CSV" [completed]="isStepValid(2)" *ngIf="extraction.extractionType === 'CSV'" [optional]="false">
        <mat-form-field class="mr-sm-2">
          <mat-label>CSV Headers</mat-label>
          <input matInput required [(ngModel)]="extraction.jsonExtractionCSV?.extractionCSVHeader">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Separator</mat-label>
          <input matInput required [(ngModel)]="extraction.jsonExtractionCSV?.extpactionCSVSeparator">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Date Format</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extractionDateFormat">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Number Format</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extractionNumberFormat">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Excluded Headers (CSVFormat)</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.jsonExtractionCSVFormat?.excludedHeaders">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Number Format (CSVFormat)</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.jsonExtractionCSVFormat?.numberFormat">
        </mat-form-field>
        <br />

        <label>SQL Query:</label>
        <textarea matInput rows="3" [(ngModel)]="extraction.jsonExtractionCSV?.jsonExtractionSQL?.extractionSQLQuery"></textarea>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext [disabled]="!isStepValid(2)">Next</button>
        </div>
      </mat-step>

      <mat-step label="XLS" [completed]="isStepValid(3)" *ngIf="extraction.extractionType === 'XLS'" [optional]="false">
        <button mat-raised-button color="primary" (click)="addSheet()">Add Sheet</button>
        <br /><br />

        <div *ngIf="extraction.jsonExtractionSheet">
          <div *ngFor="let sheet of extraction.jsonExtractionSheet; let i=index">
            <app-extraction-form-sheet [sheet]="sheet"></app-extraction-form-sheet>
            <hr />
          </div>
        </div>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext [disabled]="!isStepValid(3)">Next</button>
        </div>
      </mat-step>

      <mat-step label="Summary" optional="false">
        <h3>Summary</h3>
        <p>Name: {{extraction.extractionName}}</p>
        <p>Type: {{extraction.extractionType}}</p>
        <p>Mail? {{extraction.extractionMail ? 'Yes' : 'No'}}</p>

        <button mat-raised-button color="primary" (click)="save()">Save</button>
        <button mat-button color="warn" (click)="onCancel()">Cancel</button>
      </mat-step>
    </mat-stepper>
  </mat-card-content>
</mat-card>
