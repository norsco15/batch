import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { ExtractionService } from '../services/extraction.service';
import { JSonExtraction } from '../models/extraction.model';

@Component({
  selector: 'app-extraction-delete-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule
  ],
  templateUrl: './extraction-delete-form.component.html',
  styleUrls: ['./extraction-delete-form.component.css'],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ExtractionDeleteFormComponent implements OnInit {

  form!: FormGroup;
  extraction?: JSonExtraction;
  errorMessage?: string;

  constructor(
    private fb: FormBuilder,
    private service: ExtractionService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const st: any = history.state;
    this.extraction = st;

    this.form = this.fb.group({
      extractionId: [this.extraction?.extractionId || '']
    });
  }

  onSubmit() {
    if (!this.extraction?.extractionId) {
      this.errorMessage = 'No extractionId!';
      return;
    }

    this.service.deleteExtraction(this.extraction.extractionId.toString()).subscribe({
      next: () => {
        this.router.navigate(['/extraction/list']);
      },
      error: (err) => {
        this.errorMessage = err.message;
        console.error('Delete error', err);
      }
    });
  }

  onCancel() {
    this.router.navigate(['/extraction/list']);
  }
}
