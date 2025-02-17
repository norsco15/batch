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
    <mat-stepper orientation="horizontal">
      <!-- Step 1: GLOBAL -->
      <mat-step label="Global">
        <mat-form-field class="mr-sm-2">
          <mat-label>Extraction Name</mat-label>
          <input matInput [(ngModel)]="extraction.extractionName" name="extractionName" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Extraction Path</mat-label>
          <input matInput [(ngModel)]="extraction.extractionPath" name="extractionPath" />
        </mat-form-field>
        <br />

        <!-- extractionMail = 'Y'/'N' -->
        <mat-checkbox
          [checked]="extraction.extractionMail === 'Y'"
          (change)="toggleMail($event.checked)"
        >
          Send Mail?
        </mat-checkbox>
        <br />

        <!-- extractionType = CSV ou XLS -->
        <mat-form-field class="mr-sm-2" style="width:200px;">
          <mat-label>Extraction Type</mat-label>
          <mat-select [(ngModel)]="extraction.extractionType" name="extractionType"
                      (selectionChange)="onTypeChange()">
            <mat-option *ngFor="let t of reportTypes" [value]="t">{{ t }}</mat-option>
          </mat-select>
        </mat-form-field>

        <div>
          <button mat-button matStepperNext>Next</button>
        </div>
      </mat-step>

      <!-- Step 2: MAIL -->
      <mat-step label="Mail" *ngIf="extraction.extractionMail === 'Y'">
        <mat-form-field class="mr-sm-2">
          <mat-label>Mail Subject</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailSubject" name="mailSubject" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Mail From</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailFrom" name="mailFrom" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Mail To</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailTo" name="mailTo" />
        </mat-form-field>
        <br />

        <mat-form-field class="mr-sm-2">
          <mat-label>Mail CC</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailCc" name="mailCc" />
        </mat-form-field>
        <br />

        <mat-form-field style="width:300px;">
          <mat-label>Mail Body</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionMail?.mailBody" name="mailBody" />
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

      <!-- Step 3: CSV -->
      <mat-step label="CSV" *ngIf="extraction.extractionType === 'CSV'">
        <h3>CSV Configuration</h3>
        <mat-form-field>
          <mat-label>CSV Header</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extractionCSVHeader" name="csvHeader" />
        </mat-form-field>
        <br />

        <mat-form-field>
          <mat-label>Separator</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extpactionCSVSeparator" name="csvSeparator" />
        </mat-form-field>
        <br />

        <mat-form-field>
          <mat-label>Date Format</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extractionDateFormat" name="csvDateFormat" />
        </mat-form-field>
        <br />

        <mat-form-field>
          <mat-label>Number Format</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.extractionNumberFormat" name="csvNumberFormat" />
        </mat-form-field>
        <br />

        <h4>SQL Query</h4>
        <mat-form-field style="width:400px;">
          <mat-label>SQL Query</mat-label>
          <input matInput [(ngModel)]="extraction.jsonExtractionCSV?.jsonExtractionSQL?.extractionSQLQuery"
                 name="csvSqlQuery" />
        </mat-form-field>
        <br />

        <h4>SQL Parameters</h4>
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

      <!-- Step 4: XLS -->
      <mat-step label="XLS" *ngIf="extraction.extractionType === 'XLS'">
        <h3>XLS Configuration</h3>
        <button mat-raised-button color="accent" (click)="addSheet()">Add Sheet</button>

        <div *ngIf="extraction.jsonExtractionSheet?.length">
          <div *ngFor="let sheet of extraction.jsonExtractionSheet; let sIndex=index"
               style="border:1px solid #ccc; margin:6px; padding:6px;">
            <button mat-icon-button color="warn" style="float:right;" (click)="removeSheet(sIndex)">
              <mat-icon>delete</mat-icon>
            </button>

            <h4>Sheet #{{sIndex}} : {{ sheet.sheetName }}</h4>
            <mat-form-field>
              <mat-label>Sheet Name</mat-label>
              <input matInput [(ngModel)]="sheet.sheetName" name="sheetName{{sIndex}}" />
            </mat-form-field>
            <br />

            <h5>SQL Query</h5>
            <mat-form-field style="width:400px;">
              <mat-label>SQL Query</mat-label>
              <input matInput [(ngModel)]="sheet.jsonExtractionSQL?.extractionSQLQuery" name="xlsSqlQuery{{sIndex}}" />
            </mat-form-field>

            <h5>SQL Params</h5>
            <button mat-raised-button color="primary" (click)="addXLSParam(sIndex)">Add Param</button>
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
                <button mat-icon-button color="warn" (click)="removeXLSParam(sIndex, pIndex)">
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
                <mat-form-field style="width:250px;">
                  <mat-label>Header Name</mat-label>
                  <input matInput [(ngModel)]="h.headerName" name="headerName{{sIndex}}_{{hIndex}}" />
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
                <mat-form-field style="width:250px;">
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

      <!-- Step 5: Summary -->
      <mat-step label="Summary">
        <h3>Summary</h3>
        <p>Extraction Name: {{extraction.extractionName}}</p>
        <p>Extraction Type: {{extraction.extractionType}}</p>
        <p>Mail? {{extraction.extractionMail === 'Y' ? 'Yes' : 'No'}}</p>

        <button mat-raised-button color="primary" (click)="save()">Save</button>
        <button mat-stroked-button color="warn" (click)="cancel()">Cancel</button>
      </mat-step>
    </mat-stepper>
  </mat-card-content>
</mat-card>
