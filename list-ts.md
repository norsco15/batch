import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AgGridModule } from 'ag-grid-angular';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { ExtractionService } from '../services/extraction.service';
import { JSonExtraction } from '../models/extraction.model';

@Component({
  selector: 'app-extraction-list',
  standalone: true,
  imports: [
    CommonModule,
    AgGridModule,
    MatCardModule,
    MatButtonModule
  ],
  templateUrl: './extraction-list.component.html',
  styleUrls: ['./extraction-list.component.css'],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ExtractionListComponent implements OnInit {

  extractions: JSonExtraction[] = [];
  rowData: any[] = [];

  columnDefs: any[] = [
    { field: 'extractionId', headerName: 'ID' },
    { field: 'extractionName', headerName: 'Name' },
    { field: 'extractionType', headerName: 'Type' },
    {
      headerName: 'Edit',
      cellRenderer: (params: any) => {
        const div = document.createElement('div');
        div.innerHTML = `<cib-icon name="ic_edit" context="Update" class="ald-ico-upt"></cib-icon>`;
        div.querySelector('.ald-ico-upt')?.addEventListener('click', () => {
          this.onClickButtonUpdate(params.data);
        });
        return div;
      }
    },
    {
      headerName: 'Run',
      cellRenderer: (params: any) => {
        const div = document.createElement('div');
        div.innerHTML = `<cib-icon name="ic_arrow_right" context="Run" class="ald-ico-run"></cib-icon>`;
        div.querySelector('.ald-ico-run')?.addEventListener('click', () => {
          this.onClickButtonRun(params.data);
        });
        return div;
      }
    },
    {
      headerName: 'Delete',
      cellRenderer: (params: any) => {
        const div = document.createElement('div');
        div.innerHTML = `<cib-icon name="ic_delete" context="Delete" class="ald-ico-del"></cib-icon>`;
        div.querySelector('.ald-ico-del')?.addEventListener('click', () => {
          this.onClickButtonRemove(params.data);
        });
        return div;
      }
    },
    {
      headerName: 'Export',
      cellRenderer: (params: any) => {
        const div = document.createElement('div');
        div.innerHTML = `<cib-icon name="ic_download" context="Export" class="ald-ico-export"></cib-icon>`;
        div.querySelector('.ald-ico-export')?.addEventListener('click', () => {
          this.onClickButtonExport(params.data);
        });
        return div;
      }
    }
  ];

  constructor(
    private extractionService: ExtractionService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.extractionService.loadAllExtractions().subscribe({
      next: (data) => {
        this.extractions = data;
        this.rowData = data;
      },
      error: (err) => console.error('Error loading extractions', err)
    });
  }

  onClickButtonUpdate(extraction: JSonExtraction) {
    this.router.navigateByUrl('/extraction/update', { state: extraction });
  }

  onClickButtonRun(extraction: JSonExtraction) {
    this.router.navigateByUrl('/extraction/launch', { state: extraction });
  }

  onClickButtonRemove(extraction: JSonExtraction) {
    this.router.navigateByUrl('/extraction/delete', { state: extraction });
  }

  onClickButtonExport(extraction: JSonExtraction) {
    if (!extraction.extractionId) return;
    this.extractionService.exportExtraction(extraction.extractionId).subscribe({
      next: (data) => {
        const jsonString = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `extraction_${extraction.extractionId}.json`;
        a.click();
        URL.revokeObjectURL(url);
      },
      error: (err) => console.error('Export error', err)
    });
  }
}
