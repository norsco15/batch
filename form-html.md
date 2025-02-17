<mat-card>
  <mat-card-header>
    <mat-card-title>
      {{ formAction === 'CREATE' ? 'Create Extraction' : 'Update Extraction' }}
    </mat-card-title>
    <!-- Bouton Cancel à droite -->
    <button mat-stroked-button color="warn" style="margin-left:auto;" (click)="cancel()">
      Cancel
    </button>
  </mat-card-header>

  <mat-card-content>
    <!-- Stepper -->
    <mat-stepper orientation="horizontal">
      
      <!-- STEP 1: GLOBAL -->
      <mat-step>
        <ng-template matStepLabel>Global Parameters</ng-template>

        <!-- extractionName -->
        <mat-form-field class="mr-sm-2">
          <mat-label>Extraction Name</mat-label>
          <input matInput [(ngModel)]="extraction.extractionName" name="extractionName" required />
        </mat-form-field>
        <br />

        <!-- extractionPath -->
        <mat-form-field class="mr-sm-2">
          <mat-label>File Path</mat-label>
          <input matInput [(ngModel)]="extraction.extractionPath" name="extractionPath" />
        </mat-form-field>
        <br />

        <!-- extractionMail => 'Y' ou 'N' -->
        <mat-checkbox
          [checked]="extraction.extractionMail === 'Y'"
          (change)="extraction.extractionMail = $event.checked ? 'Y' : 'N'; toggleMail()"
        >
          Send Mail?
        </mat-checkbox>
        <br />

        <!-- extractionType => CSV ou XLS -->
        <mat-form-field class="mr-sm-2">
          <mat-label>Extraction Type</mat-label>
          <mat-select [(ngModel)]="extraction.extractionType"
                      name="extractionType"
                      (selectionChange)="onReportTypeChange()"
                      required>
            <mat-option *ngFor="let rt of reportTypesList" [value]="rt.value">
              {{ rt.label }}
            </mat-option>
          </mat-select>
        </mat-form-field>

        <div>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <!-- STEP 2: MAIL (only if extractionMail = 'Y') -->
      <mat-step *ngIf="extraction.extractionMail === 'Y'">
        <ng-template matStepLabel>Mail Data</ng-template>

        <mat-form-field class="mr-sm-2">
          <mat-label>From</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailFrom" name="mailFrom" required />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Subject</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailSubject" name="mailSubject" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Mail Body</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailBody" name="mailBody" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Mail To</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailTo" name="mailTo" required />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>CC</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailCc" name="mailCc" />
        </mat-form-field>
        <br />

        <mat-checkbox [(ngModel)]="extraction.jsonExtractionMail?.attachFile" name="attachFile">
          Attach File?
        </mat-checkbox>
        <mat-checkbox [(ngModel)]="extraction.jsonExtractionMail?.zipFile" name="zipFile">
          Zip File?
        </mat-checkbox>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <!-- STEP 3: CSV -->
      <mat-step *ngIf="extraction.extractionType === 'CSV'">
        <ng-template matStepLabel>CSV Data</ng-template>

        <!-- CSV basic fields -->
        <mat-form-field>
          <mat-label>CSV Header</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extractionCSVHeader"
                 name="csvHeader" />
        </mat-form-field>
        <br />

        <mat-form-field>
          <mat-label>Separator</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extpactionCSVSeparator"
                 name="csvSeparator" />
        </mat-form-field>
        <br />

        <mat-form-field>
          <mat-label>Date Format</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extractionDateFormat"
                 name="csvDateFormat" />
        </mat-form-field>
        <br />

        <mat-form-field>
          <mat-label>Number Format</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extractionNumberFormat"
                 name="csvNumberFormat" />
        </mat-form-field>
        <br />

        <!-- CSV Format => excludedHeaders, numberFormat -->
        <h4>CSV Format</h4>
        <mat-form-field>
          <mat-label>Excluded Headers</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.jsonExtractionCSVFormat?.excludedHeaders"
                 name="excludedHeaders" />
        </mat-form-field>
        <br />

        <mat-form-field>
          <mat-label>Excluded Number Format</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.jsonExtractionCSVFormat?.numberFormat"
                 name="excludedNumberFormat" />
        </mat-form-field>
        <br />

        <!-- SQL Query -->
        <mat-form-field style="width:400px;">
          <mat-label>SQL Query</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.jsonExtractionSQL?.extractionSQLQuery"
                 name="csvSqlQuery" />
        </mat-form-field>
        <br />

        <!-- SQL Params -->
        <h5>SQL Params</h5>
        <button mat-raised-button color="accent" (click)="addCSVParam()">Add Param</button>
        <div *ngIf="extraction.jsonExtractionCSV?.jsonExtractionSQL?.jsonExtractionSQLParameters?.length">
          <div *ngFor="let param of extraction.jsonExtractionCSV?.jsonExtractionSQL?.jsonExtractionSQLParameters; let i=index"
               style="border:1px solid #ccc; margin:4px; padding:4px;">
            <mat-form-field style="width:120px;">
              <mat-label>Type</mat-label>
              <input matInput [(ngModel)]="param.parametentype" name="csvParamType{{i}}" />
            </mat-form-field>
            <mat-form-field style="width:120px;">
              <mat-label>Name</mat-label>
              <input matInput [(ngModel)]="param.parameterName" name="csvParamName{{i}}" />
            </mat-form-field>
            <mat-form-field style="width:120px;">
              <mat-label>Value</mat-label>
              <input matInput [(ngModel)]="param.parameterValue" name="csvParamValue{{i}}" />
            </mat-form-field>
            <button mat-icon-button color="warn" (click)="removeCSVParam(i)">
              <mat-icon>delete</mat-icon>
            </button>
          </div>
        </div>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <!-- STEP 4: XLS -->
      <mat-step *ngIf="extraction.extractionType === 'XLS'">
        <ng-template matStepLabel>XLS Data</ng-template>

        <button mat-raised-button color="primary" (click)="addSheet()">Add Sheet</button>
        <br /><br />

        <div *ngIf="extraction.jsonExtractionSheet?.length">
          <div *ngFor="let sheet of extraction.jsonExtractionSheet; let sIndex=index"
               style="border:1px solid #ccc; margin:6px; padding:6px;">
            <button mat-icon-button color="warn" style="float:right;" (click)="removeSheet(sIndex)">
              <mat-icon>delete</mat-icon>
            </button>

            <mat-form-field>
              <mat-label>Sheet Name</mat-label>
              <input matInput [(ngModel)]="sheet.sheetName" name="sheetName{{sIndex}}" />
            </mat-form-field>
            <br />

            <!-- SQL Query -->
            <mat-form-field style="width:400px;">
              <mat-label>SQL Query</mat-label>
              <input matInput [(ngModel)]="sheet.jsonExtractionSQL?.extractionSQLQuery"
                     name="sheetSql{{sIndex}}" />
            </mat-form-field>

            <h5>SQL Params</h5>
            <button mat-raised-button color="accent" (click)="addXLSParam(sIndex)">Add Param</button>
            <div *ngIf="sheet.jsonExtractionSQL?.jsonExtractionSQLParameters?.length">
              <div *ngFor="let p of sheet.jsonExtractionSQL.jsonExtractionSQLParameters; let pIndex=index"
                   style="border:1px solid #ddd; margin:4px; padding:4px;">
                <mat-form-field style="width:120px;">
                  <mat-label>Type</mat-label>
                  <input matInput [(ngModel)]="p.parametentype" name="xlsParamType{{sIndex}}_{{pIndex}}" />
                </mat-form-field>
                <mat-form-field style="width:120px;">
                  <mat-label>Name</mat-label>
                  <input matInput [(ngModel)]="p.parameterName" name="xlsParamName{{sIndex}}_{{pIndex}}" />
                </mat-form-field>
                <mat-form-field style="width:120px;">
                  <mat-label>Value</mat-label>
                  <input matInput [(ngModel)]="p.parameterValue" name="xlsParamValue{{sIndex}}_{{pIndex}}" />
                </mat-form-field>
                <button mat-icon-button color="warn" (click)="removeXLSParam(sIndex,pIndex)">
                  <mat-icon>delete</mat-icon>
                </button>
              </div>
            </div>

            <h5>Headers</h5>
            <button mat-raised-button color="primary" (click)="addHeader(sIndex)">Add Header</button>
            <div *ngIf="sheet.jsonExtractionSheetHeader?.length">
              <div *ngFor="let h of sheet.jsonExtractionSheetHeader; let hIndex=index"
                   style="border:1px solid #eee; margin:4px; padding:4px;">
                <button mat-icon-button color="warn" style="float:right;" (click)="removeHeader(sIndex,hIndex)">
                  <mat-icon>delete</mat-icon>
                </button>
                <mat-form-field style="width:200px;">
                  <mat-label>Header Name</mat-label>
                  <input matInput [(ngModel)]="h.headerName"
                         name="headerName{{sIndex}}_{{hIndex}}" />
                </mat-form-field>
              </div>
            </div>

            <h5>Fields</h5>
            <button mat-raised-button color="primary" (click)="addField(sIndex)">Add Field</button>
            <div *ngIf="sheet.jsonExtractionSheetField?.length">
              <div *ngFor="let f of sheet.jsonExtractionSheetField; let fIndex=index"
                   style="border:1px solid #eee; margin:4px; padding:4px;">
                <button mat-icon-button color="warn" style="float:right;" (click)="removeField(sIndex,fIndex)">
                  <mat-icon>delete</mat-icon>
                </button>
                <mat-form-field style="width:200px;">
                  <mat-label>Field Name</mat-label>
                  <input matInput [(ngModel)]="f.fieldName" name="fieldName{{sIndex}}_{{fIndex}}" />
                </mat-form-field>
              </div>
            </div>

          </div>
        </div>

        <div>
          <button mat-button matStepperPrevious>Back</button>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <!-- STEP 5: SUMMARY -->
      <mat-step>
        <ng-template matStepLabel>Summary</ng-template>

        <h3>Summary</h3>
        <p>Name: {{extraction.extractionName}}</p>
        <p>Type: {{extraction.extractionType}}</p>
        <p>Mail? {{extraction.extractionMail === 'Y' ? 'Yes' : 'No'}}</p>

        <button mat-raised-button color="primary" (click)="save()">Save</button>
        <button mat-stroked-button color="warn" (click)="cancel()">Cancel</button>
      </mat-step>
    </mat-stepper>
  </mat-card-content>
</mat-card>
