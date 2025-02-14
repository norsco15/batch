<mat-card>
  <mat-card-header>
    <mat-card-title>Launch Extraction</mat-card-title>
  </mat-card-header>

  <mat-card-content>
    <form [formGroup]="form" (ngSubmit)="onSubmit()">

      <mat-form-field>
        <mat-label>Extraction ID</mat-label>
        <input matInput formControlName="extractionId" disabled />
      </mat-form-field>

      <p>Parameters (optional):</p>
      <div formArrayName="params">
        <div *ngFor="let paramGroup of paramsArray.controls; let i=index" [formGroupName]="i">
          <mat-form-field>
            <mat-label>Parameter Name</mat-label>
            <input matInput formControlName="parameterName" />
          </mat-form-field>

          <mat-form-field>
            <mat-label>Parameter Value</mat-label>
            <input matInput formControlName="parameterValue" />
          </mat-form-field>

          <button mat-icon-button color="warn" (click)="removeParam(i)">
            <mat-icon>delete</mat-icon>
          </button>
        </div>
      </div>

      <button mat-raised-button color="accent" type="button" (click)="addParam()">
        Add Parameter
      </button>

      <br /><br />

      <p>Do you want to launch this extraction?</p>
      <button mat-raised-button color="primary" type="submit">Yes</button>
      <button mat-button color="warn" type="button" (click)="onCancel()">Cancel</button>

      <p style="color:red;">{{ errorMessage }}</p>
    </form>
  </mat-card-content>
</mat-card>
