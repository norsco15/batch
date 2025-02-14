import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, FormControl, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { ExtractionService } from '../services/extraction.service';
import { JSonExtraction, JSonLaunchExtraction, JSonExtractionParameters } from '../models/extraction.model';

@Component({
  selector: 'app-extraction-launch-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule
  ],
  templateUrl: './extraction-launch-form.component.html',
  styleUrls: ['./extraction-launch-form.component.css'],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ExtractionLaunchFormComponent implements OnInit {

  extraction?: JSonExtraction;
  form!: FormGroup;
  errorMessage?: string;

  get paramsArray(): FormArray {
    return this.form.get('params') as FormArray;
  }

  constructor(
    private fb: FormBuilder,
    private service: ExtractionService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const st: any = history.state;
    this.extraction = st;

    this.form = this.fb.group({
      extractionId: [this.extraction?.extractionId || ''],
      params: this.fb.array([])
    });
  }

  addParam() {
    this.paramsArray.push(
      this.fb.group({
        parameterName: [''],
        parameterValue: ['']
      })
    );
  }

  removeParam(index: number) {
    this.paramsArray.removeAt(index);
  }

  onSubmit() {
    if (!this.extraction?.extractionId) {
      this.errorMessage = 'No extractionId found';
      return;
    }
    const paramList: JSonExtractionParameters[] = this.paramsArray.value;
    const launchObj: JSonLaunchExtraction = {
      extractionId: this.extraction.extractionId,
      extractionParameters: paramList
    };

    this.service.launchExtraction(launchObj).subscribe({
      next: () => {
        this.router.navigate(['/extraction/list']);
      },
      error: (err) => {
        this.errorMessage = err.message;
        console.error('Error launching extraction', err);
      }
    });
  }

  onCancel() {
    this.router.navigate(['/extraction/list']);
  }
}
