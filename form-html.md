<mat-card>
  <mat-card-header>
    <mat-card-title>
      {{ formAction === 'CREATE' ? 'Create Extraction' : 'Update Extraction' }}
    </mat-card-title>
  </mat-card-header>

  <mat-card-content>
    <mat-stepper #stepper orientation="horizontal">

      <!-- Step 1: Param généraux -->
      <mat-step label="Global">
        <input type="hidden" [(ngModel)]="extraction.extractionId" />

        <mat-form-field class="mr-sm-2">
          <mat-label>Report Name</mat-label>
          <input matInput [(ngModel)]="extraction.extractionName" />
        </mat-form-field>

        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>File Path (optionnel)</mat-label>
          <input matInput [(ngModel)]="extraction.extractionPath" />
        </mat-form-field>

        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Format</mat-label>
          <mat-select [(ngModel)]="extraction.extractionType" (selectionChange)="onReportTypeChange()">
            <mat-option *ngFor="let rt of reportTypesList" [value]="rt.value">
              {{ rt.label }}
            </mat-option>
          </mat-select>
        </mat-form-field>

        <br />

        <mat-checkbox [(ngModel)]="extraction.jsonExtractionMail" (change)="toggleMail()">
          Send Mail ?
        </mat-checkbox>

        <div>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <!-- Step 2: Mail si jsonExtractionMail -->
      <mat-step label="Mail" *ngIf="extraction.jsonExtractionMail">
        <mat-form-field class="mr-sm-2">
          <mat-label>From</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail.mailFrom" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Subject</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail.mailSubject" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>To</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail.mailTo" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>CC</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail.mailCc" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Mail Body</mat-label>
          <textarea matInput [(ngModel)]="extraction.jsonExtractionMail.mailBody"></textarea>
        </mat-form-field>
        <br />

        <mat-checkbox [(ngModel)]="extraction.jsonExtractionMail.attachFile">Attach File ?</mat-checkbox>
        <mat-checkbox [(ngModel)]="extraction.jsonExtractionMail.zipFile">Zip File ?</mat-checkbox>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <!-- Step 3: CSV -->
      <mat-step label="CSV" *ngIf="extraction.extractionType === 'CSV'">
        <mat-form-field class="mr-sm-2">
          <mat-label>CSV Headers</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV.extractionCSVHeader" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Separator</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV.extpactionCSVSeparator" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Date Format</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV.extractionDateFormat" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Number Format</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV.extractionNumberFormat" />
        </mat-form-field>
        <br />

        <label>SQL Query</label>
        <textarea matInput rows="3" [(ngModel)]="extraction.jsonExtractionCSV.jsonExtractionSQL.extractionSQLQuery"></textarea>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <!-- Step 4: XLS => on délègue à un composant "extraction-form-sheet" -->
      <mat-step label="XLS" *ngIf="extraction.extractionType === 'XLS'">
        <!-- On peut juste insérer un bouton pour addSheet + 
             un *ngFor pour afficher extraction-form-sheet sur chaque sheet -->
        <button mat-raised-button color="primary" (click)="addSheet()">Add Sheet</button>
        <br /><br />

        <div *ngIf="extraction.jsonExtractionSheet?.length">
          <div *ngFor="let sheet of extraction.jsonExtractionSheet; let i = index">
            <!-- On utilise le composant fils -->
            <app-extraction-form-sheet
              [sheet]="sheet">
            </app-extraction-form-sheet>

            <hr />
          </div>
        </div>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <!-- Step 5: Summary -->
      <mat-step label="Summary">
        <h3>Summary</h3>
        <p>Extraction Name: {{extraction.extractionName}}</p>
        <p>Type: {{extraction.extractionType}}</p>
        <p>Mail?: {{extraction.jsonExtractionMail ? 'Yes' : 'No'}}</p>

        <p *ngIf="extraction.extractionType === 'CSV'">
          CSV Header: {{extraction.jsonExtractionCSV?.extractionCSVHeader}}
        </p>

        <p *ngIf="extraction.extractionType === 'XLS'">
          Sheets: {{extraction.jsonExtractionSheet?.length}}
        </p>

        <button mat-raised-button color="primary" (click)="save()">Save</button>
        <button mat-button color="warn" [routerLink]="'/admin/extraction/list'">Cancel</button>
      </mat-step>

    </mat-stepper>
  </mat-card-content>
</mat-card>
