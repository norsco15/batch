import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
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
    MatInputModule,
    RouterLink
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
    private formBuilder: FormBuilder,
    private service: ExtractionService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // On récupère l'extraction via history.state
    const state: any = history.state;
    this.extraction = state;

    this.form = this.formBuilder.group({
      fieldExtractionId: [this.extraction?.extractionId || '']
    });
  }

  onSubmit() {
    if (!this.extraction?.extractionId) {
      this.errorMessage = 'No extractionId provided!';
      return;
    }
    // Appel service
    this.service.deleteExtraction(this.extraction.extractionId.toString())
      .subscribe({
        next: () => {
          this.router.navigate(['/extraction/list']);
        },
        error: (err) => {
          this.errorMessage = err.message;
          console.error('Error deleting extraction', err);
        }
      });
  }
}
