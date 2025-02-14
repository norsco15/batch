<h2 mat-dialog-title>
  {{ data.isHeader ? 'Edit Header Style' : 'Edit Field Style' }}
</h2>

<mat-dialog-content>
  <!-- si c'est header -->
  <div *ngIf="data.isHeader">
    <mat-form-field>
      <mat-label>Header Name</mat-label>
      <input matInput [(ngModel)]="data.header.headerName">
    </mat-form-field>

    <h3>Cell Style</h3>
    <!-- On vérifie que data.header.jsonExtractionCellStyle existe -->
    <ng-container *ngIf="data.header.jsonExtractionCellStyle; else createStyleHeader">
      <app-style-form [cellStyle]="data.header.jsonExtractionCellStyle"></app-style-form>
      <!-- un composant "app-style-form" si vous voulez détailler. 
           Sinon on met tout ici. -->
    </ng-container>
    <ng-template #createStyleHeader>
      <button mat-button (click)="data.header.jsonExtractionCellStyle = {}; ">Create Style</button>
    </ng-template>
  </div>

  <!-- si c'est field -->
  <div *ngIf="!data.isHeader">
    <mat-form-field>
      <mat-label>Field Name</mat-label>
      <input matInput [(ngModel)]="data.field.fieldName">
    </mat-form-field>

    <h3>Cell Style</h3>
    <ng-container *ngIf="data.field.jsonExtractionCellStyle; else createStyleField">
      <!-- style editing toggles, color, etc. -->
      <app-style-form [cellStyle]="data.field.jsonExtractionCellStyle"></app-style-form>
    </ng-container>
    <ng-template #createStyleField>
      <button mat-button (click)="data.field.jsonExtractionCellStyle = {}; ">Create Style</button>
    </ng-template>
  </div>
</mat-dialog-content>

<mat-dialog-actions>
  <button mat-button (click)="onCancel()">Cancel</button>
  <button mat-raised-button color="primary" (click)="onSave()">Save</button>
</mat-dialog-actions>
