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

      <h4>Parameters</h4>
      <div formArrayName="params">
        <div *ngFor="let grp of paramsArray.controls; let i=index" [formGroupName]="i" style="border:1px solid #ccc; margin:4px; padding:4px;">
          <mat-form-field style="width:200px;">
            <mat-label>Name</mat-label>
            <input matInput formControlName="parameterName" />
          </mat-form-field>
          <mat-form-field style="width:200px;">
            <mat-label>Value</mat-label>
            <input matInput formControlName="parameterValue" />
          </mat-form-field>

          <button mat-icon-button color="warn" (click)="removeParam(i)">
            <mat-icon>delete</mat-icon>
          </button>
        </div>
      </div>

      <button mat-raised-button color="accent" type="button" (click)="addParam()">Add Param</button>

      <br /><br />

      <p>Do you want to launch this extraction?</p>
      <button mat-raised-button color="primary" type="submit">Yes</button>
      <button mat-stroked-button color="warn" type="button" (click)="onCancel()">Cancel</button>

      <p style="color:red;">{{ errorMessage }}</p>
    </form>
  </mat-card-content>
</mat-card>
