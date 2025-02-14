import { Component, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';

import { JSonExtractionSheet, JSonExtractionSheetHeader, JSonExtractionSheetField } from '../models/extraction.model';
// import { ExtractionColumnDialogComponent } from './extraction-column-dialog.component'; // si vous voulez ouvrir un dialog

@Component({
  selector: 'app-extraction-form-sheet',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule
  ],
  templateUrl: './extraction-form-sheet.component.html',
  styleUrls: ['./extraction-form-sheet.component.css']
})
export class ExtractionFormSheetComponent implements OnInit {

  @Input() sheet!: JSonExtractionSheet;

  constructor(
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
  }

  addHeader() {
    if (!this.sheet.jsonExtractionSheetHeader) {
      this.sheet.jsonExtractionSheetHeader = [];
    }
    const order = this.sheet.jsonExtractionSheetHeader.length;
    this.sheet.jsonExtractionSheetHeader.push({
      extractionSheetHeaderId: undefined,
      headerOrder: BigInt(order),
      headerName: 'HEADER' + order,
      jsonExtractionCellStyle: undefined
    });
  }

  addField() {
    if (!this.sheet.jsonExtractionSheetField) {
      this.sheet.jsonExtractionSheetField = [];
    }
    const order = this.sheet.jsonExtractionSheetField.length;
    this.sheet.jsonExtractionSheetField.push({
      extractionSheetFieldId: undefined,
      fieldorder: BigInt(order),
      fieldName: 'FIELD' + order,
      fieldFormat: '',
      jsonExtractionCellStyle: undefined
    });
  }

  editHeader(h: JSonExtractionSheetHeader) {
    // Ouvrir un dialog ou autre logic
    // const dialogRef = this.dialog.open(ExtractionColumnDialogComponent, {
    //   data: { isHeader: true, header: h },
    // });
  }

  editField(f: JSonExtractionSheetField) {
    // const dialogRef = this.dialog.open(ExtractionColumnDialogComponent, {
    //   data: { isHeader: false, field: f },
    // });
  }
}
