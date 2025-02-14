<mat-form-field>
  <mat-label>Sheet Name</mat-label>
  <input matInput [(ngModel)]="sheet.sheetName">
</mat-form-field>

<br />
<label>SQL Query:</label>
<textarea matInput rows="2" [(ngModel)]="sheet.jsonExtractionSQL.extractionSQLQuery"></textarea>

<hr />

<h4>Headers</h4>
<button mat-raised-button color="primary" (click)="addHeader()">Add Header</button>
<div *ngIf="sheet.jsonExtractionSheetHeader?.length">
  <div *ngFor="let h of sheet.jsonExtractionSheetHeader; let i=index" style="border:1px solid #ccc; margin-top:5px;">
    <p>Header #{{i}}: {{ h.headerName }} (Order: {{h.headerOrder}})</p>
    <button mat-icon-button color="primary" (click)="editHeader(h)">
      <mat-icon>edit</mat-icon>
    </button>
  </div>
</div>

<hr />

<h4>Fields</h4>
<button mat-raised-button color="primary" (click)="addField()">Add Field</button>
<div *ngIf="sheet.jsonExtractionSheetField?.length">
  <div *ngFor="let f of sheet.jsonExtractionSheetField; let j=index" style="border:1px solid #ccc; margin-top:5px;">
    <p>Field #{{j}}: {{ f.fieldName }} (Order: {{f.fieldorder}})</p>
    <button mat-icon-button color="primary" (click)="editField(f)">
      <mat-icon>edit</mat-icon>
    </button>
  </div>
</div>
