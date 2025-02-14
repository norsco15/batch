import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-extraction-column-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatButtonToggleModule,
    MatButtonModule
  ],
  templateUrl: './extraction-column-dialog.component.html',
  styleUrls: ['./extraction-column-dialog.component.css']
})
export class ExtractionColumnDialogComponent {

  // data.isHeader = boolean
  // data.header ou data.field
  constructor(
    public dialogRef: MatDialogRef<ExtractionColumnDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  onCancel(): void {
    this.dialogRef.close();
  }

  onSave(): void {
    // on peut renvoyer data.header ou data.field modifié
    this.dialogRef.close({ ...this.data });
  }
}
