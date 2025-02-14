<!-- Nom du sheet -->
<mat-form-field class="mr-sm-2">
  <mat-label>Sheet Name</mat-label>
  <input matInput [(ngModel)]="sheet.sheetName" />
</mat-form-field>

<br />

<!-- SQL du sheet -->
<label>SQL Query:</label>
<textarea matInput rows="3" [(ngModel)]="sheet.jsonExtractionSQL.extractionSQLQuery"></textarea>

<hr />

<!-- Headers -->
<h4>Headers</h4>
<button mat-raised-button color="primary" (click)="addHeader()">Add Header</button>
<div *ngIf="sheet.jsonExtractionSheetHeader?.length">
  <div *ngFor="let h of sheet.jsonExtractionSheetHeader; let i = index" style="border: 1px solid #ccc; padding: 5px; margin-top: 5px;">
    <p>Header #{{i}} : {{ h.headerName }} (order: {{h.headerOrder}})</p>
    <button mat-icon-button color="primary" (click)="editHeader(h)">
      <mat-icon>edit</mat-icon>
    </button>
  </div>
</div>

<hr />

<!-- Fields -->
<h4>Fields</h4>
<button mat-raised-button color="primary" (click)="addField()">Add Field</button>
<div *ngIf="sheet.jsonExtractionSheetField?.length">
  <div *ngFor="let f of sheet.jsonExtractionSheetField; let j = index" style="border: 1px solid #ccc; padding: 5px; margin-top: 5px;">
    <p>Field #{{j}} : {{ f.fieldName }} (order: {{f.fieldorder}})</p>
    <button mat-icon-button color="primary" (click)="editField(f)">
      <mat-icon>edit</mat-icon>
    </button>
  </div>
</div>
