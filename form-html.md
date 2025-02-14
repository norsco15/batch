<mat-card>
  <mat-card-header>
    <mat-card-title>
      {{ formAction === 'CREATE' ? 'Create Extraction' : 'Update Extraction' }}
    </mat-card-title>
  </mat-card-header>

  <mat-card-content>
    <mat-stepper #stepper orientation="horizontal">

      <mat-step label="Global">
        <input type="hidden" [(ngModel)]="extraction.extractionId">

        <mat-form-field class="mr-sm-2">
          <mat-label>Report Name</mat-label>
          <input matInput [(ngModel)]="extraction.extractionName">
        </mat-form-field>

        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>File Path</mat-label>
          <input matInput [(ngModel)]="extraction.extractionPath">
        </mat-form-field>

        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Report Type</mat-label>
          <mat-select [(ngModel)]="extraction.extractionType" (selectionChange)="onReportTypeChange()">
            <mat-option *ngFor="let rt of reportTypesList" [value]="rt.value">
              {{ rt.label }}
            </mat-option>
          </mat-select>
        </mat-form-field>

        <br />

        <mat-checkbox [(ngModel)]="extraction.extractionMail" (change)="toggleMail()">
          Send Mail ?
        </mat-checkbox>

        <div>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <mat-step label="Mail" *ngIf="extraction.extractionMail && extraction.jsonExtractionMail">
        <mat-form-field class="mr-sm-2">
          <mat-label>From</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail.mailFrom">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Subject</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail.mailSubject">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>To</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail.mailTo">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>CC</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail.mailCc">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Body</mat-label>
          <textarea matInput [(ngModel)]="extraction.jsonExtractionMail.mailBody"></textarea>
        </mat-form-field>
        <br />

        <mat-checkbox [(ngModel)]="extraction.jsonExtractionMail.attachFile">Attach File?</mat-checkbox>
        <mat-checkbox [(ngModel)]="extraction.jsonExtractionMail.zipFile">Zip File?</mat-checkbox>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <mat-step label="CSV" *ngIf="extraction.extractionType === 'CSV'">
        <mat-form-field class="mr-sm-2">
          <mat-label>Headers</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extractionCSVHeader">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Separator</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extpactionCSVSeparator">
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

        <!-- CSVFormat => excludedHeaders, numberFormat -->
        <mat-form-field class="mr-sm-2">
          <mat-label>Excluded Headers (CSVFormat)</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.jsonExtractionCSVFormat?.excludedHeaders">
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Number Format (CSVFormat) for excludedHeaders</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.jsonExtractionCSVFormat?.numberFormat">
        </mat-form-field>
        <br />

        <label>SQL Query:</label>
        <textarea matInput rows="3" [(ngModel)]="extraction.jsonExtractionCSV?.jsonExtractionSQL?.extractionSQLQuery"></textarea>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <mat-step label="XLS" *ngIf="extraction.extractionType === 'XLS'">
        <button mat-raised-button color="primary" (click)="addSheet()">Add Sheet</button>
        <br /><br />
        <div *ngIf="extraction.jsonExtractionSheet">
          <div *ngFor="let sheet of extraction.jsonExtractionSheet; let i = index">
            <app-extraction-form-sheet [sheet]="sheet"></app-extraction-form-sheet>
            <hr />
          </div>
        </div>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <mat-step label="Summary">
        <h3>Summary</h3>
        <p>Name: {{extraction.extractionName}}</p>
        <p>Type: {{extraction.extractionType}}</p>
        <p>Mail?: {{extraction.extractionMail ? 'Yes' : 'No'}}</p>
        
        <button mat-raised-button color="primary" (click)="save()">Save</button>
        <button mat-button color="warn" [routerLink]="'/extraction/list'">Cancel</button>
      </mat-step>

    </mat-stepper>
  </mat-card-content>
</mat-card>
