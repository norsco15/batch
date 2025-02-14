import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
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
  rowData: any[] = [];

  columnDefs: any[] = [
    { field: 'extractionId', headerName: 'ID' },
    { field: 'extractionName', headerName: 'Name' },
    { field: 'extractionType', headerName: 'Type' },
    {
      headerName: 'Actions',
      cellRenderer: (params: any) => {
        const container = document.createElement('div');
        container.style.display = 'flex';
        container.style.gap = '8px';

        // Icon stylo => update
        const editIcon = document.createElement('i');
        editIcon.className = 'fas fa-pen'; // ou cib-icon si vous voulez
        editIcon.style.cursor = 'pointer';
        editIcon.addEventListener('click', () => this.onClickButtonUpdate(params.data));
        container.appendChild(editIcon);

        // Icon corbeille => delete
        const deleteIcon = document.createElement('i');
        deleteIcon.className = 'fas fa-trash';
        deleteIcon.style.cursor = 'pointer';
        deleteIcon.addEventListener('click', () => this.onClickButtonRemove(params.data));
        container.appendChild(deleteIcon);

        // Icon triangle => launch
        const launchIcon = document.createElement('i');
        launchIcon.className = 'fas fa-play';
        launchIcon.style.cursor = 'pointer';
        launchIcon.addEventListener('click', () => this.onClickButtonLaunch(params.data));
        container.appendChild(launchIcon);

        // Icon export => export
        const exportIcon = document.createElement('i');
        exportIcon.className = 'fas fa-download';
        exportIcon.style.cursor = 'pointer';
        exportIcon.addEventListener('click', () => this.onClickButtonExport(params.data));
        container.appendChild(exportIcon);

        return container;
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
      error: (err) => {
        console.error('Error loading extractions', err);
      }
    });
  }

  onClickButtonUpdate(extraction: JSonExtraction) {
    this.router.navigateByUrl('/extraction/update', { state: extraction });
  }

  onClickButtonRemove(extraction: JSonExtraction) {
    this.router.navigateByUrl('/extraction/delete', { state: extraction });
  }

  onClickButtonLaunch(extraction: JSonExtraction) {
    this.router.navigateByUrl('/extraction/launch', { state: extraction });
  }

  onClickButtonExport(extraction: JSonExtraction) {
    // Appeler l'API pour obtenir le JSON et le télécharger
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
      error: (err) => {
        console.error('Error exporting extraction', err);
      }
    });
  }
}
