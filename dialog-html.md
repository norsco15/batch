<h2 mat-dialog-title>
  {{ data.isHeader ? 'Edit Header' : 'Edit Field' }}
</h2>

<mat-dialog-content>
  <div *ngIf="data.isHeader">
    <mat-form-field>
      <mat-label>Header Name</mat-label>
      <input matInput [(ngModel)]="data.header.headerName">
    </mat-form-field>
    <!-- Ajouter la partie style: backgroundColor, alignement, etc. -->
  </div>

  <div *ngIf="!data.isHeader">
    <mat-form-field>
      <mat-label>Field Name</mat-label>
      <input matInput [(ngModel)]="data.field.fieldName">
    </mat-form-field>
    <!-- Idem style etc. -->
  </div>
</mat-dialog-content>

<mat-dialog-actions>
  <button mat-button (click)="onCancel()">Cancel</button>
  <button mat-raised-button color="primary" (click)="onSave()">Save</button>
</mat-dialog-actions>
