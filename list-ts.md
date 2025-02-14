import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AgGridModule } from 'ag-grid-angular';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';

import { ExtractionService } from '../services/extraction.service'; // A adapter
import { JSonExtraction } from '../models/extraction.model';

@Component({
  selector: 'app-extraction-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterLinkActive,
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

  columnDefs: any[] = [
    { field: 'extractionId', headerName: 'ID' },
    { field: 'extractionName', headerName: 'Name' },
    { field: 'extractionType', headerName: 'Type' },
    {
      headerName: 'Update',
      cellRenderer: (params: any) => {
        const div = document.createElement('div');
        div.innerHTML = `<button class="btn-update">Update</button>`;
        div.querySelector('.btn-update')?.addEventListener('click', () => {
          this.onClickButtonUpdateAction(params.data);
        });
        return div;
      }
    },
    {
      headerName: 'Delete',
      cellRenderer: (params: any) => {
        const div = document.createElement('div');
        div.innerHTML = `<button class="btn-delete">Delete</button>`;
        div.querySelector('.btn-delete')?.addEventListener('click', () => {
          this.onClickButtonRemoveAction(params.data);
        });
        return div;
      }
    },
    {
      headerName: 'Launch',
      cellRenderer: (params: any) => {
        const div = document.createElement('div');
        div.innerHTML = `<button class="btn-launch">Launch</button>`;
        div.querySelector('.btn-launch')?.addEventListener('click', () => {
          this.onClickButtonLaunchAction(params.data);
        });
        return div;
      }
    }
  ];

  rowData: any[] = [];

  constructor(
    private extractionService: ExtractionService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.extractionService.loadAllExtractions().subscribe({
      next: (data) => {
        this.extractions = data;
        this.rowData = data; // pour ag-grid
      },
      error: (err) => {
        console.error('Error loading extractions', err);
      }
    });
  }

  onClickButtonUpdateAction(extraction: JSonExtraction) {
    this.router.navigateByUrl('/extraction/update', { state: extraction });
  }

  onClickButtonRemoveAction(extraction: JSonExtraction) {
    this.router.navigateByUrl('/extraction/delete', { state: extraction });
  }

  onClickButtonLaunchAction(extraction: JSonExtraction) {
    this.router.navigateByUrl('/extraction/launch', { state: extraction });
  }
}
