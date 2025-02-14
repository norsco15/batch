import { Component, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { JSonExtractionSheet, JSonExtractionSheetHeader, JSonExtractionSheetField } from '../models/extraction.model';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { ExtractionColumnDialogComponent } from './extraction-column-dialog.component';

@Component({
  selector: 'app-extraction-form-sheet',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatDialogModule,
    MatIconModule
  ],
  templateUrl: './extraction-form-sheet.component.html',
  styleUrls: ['./extraction-form-sheet.component.css']
})
export class ExtractionFormSheetComponent implements OnInit {

  @Input()
  sheet!: JSonExtractionSheet;  // on suppose qu'on a un sheet non nul

  constructor(private dialog: MatDialog) { }

  ngOnInit(): void {
    // console.log('Sheet loaded', this.sheet);
  }

  addHeader() {
    if (!this.sheet.jsonExtractionSheetHeader) {
      this.sheet.jsonExtractionSheetHeader = [];
    }
    const order = BigInt(this.sheet.jsonExtractionSheetHeader.length);
    this.sheet.jsonExtractionSheetHeader.push({
      extractionSheetHeaderId: undefined,
      headerOrder: order,
      headerName: 'HEADER' + order,
      jsonExtractionCellStyle: undefined
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
      fieldName: 'FIELD' + order,
      fieldFormat: '',
      jsonExtractionCellStyle: undefined
    });
  }

  editHeader(header: JSonExtractionSheetHeader) {
    // Ouvrir un dialog
    const dialogRef = this.dialog.open(ExtractionColumnDialogComponent, {
      data: {
        isHeader: true,
        header
      },
      width: '600px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // On met à jour ? Normalement, result = { header: ...modifié... }
      }
    });
  }

  editField(field: JSonExtractionSheetField) {
    const dialogRef = this.dialog.open(ExtractionColumnDialogComponent, {
      data: {
        isHeader: false,
        field
      },
      width: '600px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // On met à jour si besoin
      }
    });
  }
}
