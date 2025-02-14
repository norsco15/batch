<h2 mat-dialog-title>
  {{ data.isHeader ? 'Edit Header Style' : 'Edit Field Style' }}
</h2>

<mat-dialog-content>
  <p *ngIf="data.isHeader">
    Header Name:
    <input matInput [(ngModel)]="data.header.headerName" />
  </p>
  <p *ngIf="!data.isHeader">
    Field Name:
    <input matInput [(ngModel)]="data.field.fieldName" />
  </p>

  <p>
    Background Color:
    <mat-form-field>
      <mat-select [value]="data.isHeader ? data.header.jsonExtractionCellStyle?.backgroundColor : data.field.jsonExtractionCellStyle?.backgroundColor">
        <mat-option [value]="'WHITE'">White</mat-option>
        <mat-option [value]="'RED'">Red</mat-option>
        <mat-option [value]="'GREEN'">Green</mat-option>
        <mat-option [value]="'BLUE'">Blue</mat-option>
      </mat-select>
    </mat-form-field>
  </p>

  <!-- etc. pour font, border, alignment, ... -->
</mat-dialog-content>

<mat-dialog-actions>
  <button mat-button (click)="onCancel()">Cancel</button>
  <button mat-button color="primary" (click)="onSave()">Save</button>
</mat-dialog-actions>
