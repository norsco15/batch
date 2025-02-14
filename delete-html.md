<mat-card>
  <mat-card-header>
    <mat-card-title>Delete Extraction</mat-card-title>
  </mat-card-header>

  <mat-card-content>
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <mat-form-field class="mr-sm-2">
        <mat-label>Extraction ID</mat-label>
        <input matInput formControlName="fieldExtractionId" disabled />
      </mat-form-field>

      <p>Do you really want to delete this extraction?</p>

      <div style="display: flex; gap: 1rem;">
        <button mat-raised-button color="primary" type="submit">
          Yes
        </button>
        <button mat-stroked-button color="warn" [routerLink]="'/extraction/list'">
          Cancel
        </button>
      </div>

      <p style="color:red;">{{ errorMessage }}</p>
    </form>
  </mat-card-content>
</mat-card>
