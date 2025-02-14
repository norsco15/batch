import { Component, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';

import { JSonExtractionSheet, JSonExtractionSheetHeader, JSonExtractionSheetField } from '../models/extraction.model';
import { ExtractionColumnDialogComponent } from './extraction-column-dialog.component';

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

  constructor(private dialog: MatDialog) {}

  ngOnInit(): void {}

  addHeader() {
    if (!this.sheet.jsonExtractionSheetHeader) {
      this.sheet.jsonExtractionSheetHeader = [];
    }
    const order = BigInt(this.sheet.jsonExtractionSheetHeader.length);
    this.sheet.jsonExtractionSheetHeader.push({
      extractionSheetHeaderId: undefined,
      headerOrder: order,
      headerName: 'HEADER ' + order,
      jsonExtractionCellStyle: {}
    });
  }

  addField() {
    if (!this.sheet.jsonExtractionSheetField) {
      this.sheet.jsonExtractionSheetField = [];
    }
    const order = BigInt(this.sheet.jsonExtractionSheetField.length);
    this.sheet.jsonExtractionSheetField.push({
      extractionSheetFieldId: undefined,
      fieldorder: order,
      fieldName: 'FIELD ' + order,
      fieldFormat: '',
      jsonExtractionCellStyle: {}
    });
  }

  editHeader(h: JSonExtractionSheetHeader) {
    const dialogRef = this.dialog.open(ExtractionColumnDialogComponent, {
      data: {
        isHeader: true,
        header: h
      },
      width: '800px'
    });
  }

  editField(f: JSonExtractionSheetField) {
    const dialogRef = this.dialog.open(ExtractionColumnDialogComponent, {
      data: {
        isHeader: false,
        field: f
      },
      width: '800px'
    });
  }
}
