import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';

@Component({
  selector: 'app-extraction-column-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatSelectModule
  ],
  templateUrl: './extraction-column-dialog.component.html',
  styleUrls: ['./extraction-column-dialog.component.css']
})
export class ExtractionColumnDialogComponent implements OnInit {

  constructor(
    public dialogRef: MatDialogRef<ExtractionColumnDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  ngOnInit(): void {
    // data = { isHeader: boolean, header?: JSonExtractionSheetHeader, field?: JSonExtractionSheetField }
  }

  onCancel() {
    this.dialogRef.close();
  }

  onSave() {
    // On renvoie data modifié
    this.dialogRef.close(this.data);
  }
}
