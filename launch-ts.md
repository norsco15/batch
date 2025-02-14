import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { ExtractionService } from '../services/extraction.service';
import { JSonExtraction, JSonLaunchExtraction } from '../models/extraction.model';

@Component({
  selector: 'app-extraction-launch-form',
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
  templateUrl: './extraction-launch-form.component.html',
  styleUrls: ['./extraction-launch-form.component.css'],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ExtractionLaunchFormComponent implements OnInit {

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
      // Ajouter d'autres champs si on veut paramétrer le job
    });
  }

  onSubmit() {
    if (!this.extraction?.extractionId) {
      this.errorMessage = 'No extractionId found!';
      return;
    }

    const launchObj: JSonLaunchExtraction = {
      extractionId: this.extraction.extractionId
      // extractionParameters?: ...
    };
    // Appel au service
    this.service.launchExtraction(launchObj).subscribe({
      next: () => {
        // success => on revient à la liste
        this.router.navigate(['/extraction/list']);
      },
      error: (err) => {
        this.errorMessage = err.message;
        console.error('Error launching extraction', err);
      }
    });
  }
}
