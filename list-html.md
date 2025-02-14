<mat-card>
  <mat-card-header>
    <mat-card-title>List of all extractions</mat-card-title>

    <button mat-raised-button color="primary" [routerLink]="'/extraction/create'">
      Create
    </button>
  </mat-card-header>

  <mat-card-content>
    <ag-grid-angular
      style="width: 100%; height: 600px; border:1px solid #DDDDDD; border-radius: 4px;"
      class="ag-theme-alpine mt-sm-3"
      [rowData]="rowData"
      [columnDefs]="columnDefs"
      enableCellTextSelection="true">
    </ag-grid-angular>
  </mat-card-content>
</mat-card>
