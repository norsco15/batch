import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  JSonExtraction,
  JSonLaunchExtraction
} from '../models/extraction.model';

@Injectable({ providedIn: 'root' })
export class ExtractionService {

  private baseUrl = '/api/extraction';

  constructor(private http: HttpClient) {}

  loadAllExtractions(): Observable<JSonExtraction[]> {
    return this.http.get<JSonExtraction[]>(`${this.baseUrl}/load_all`);
  }

  createExtraction(extraction: JSonExtraction): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/save`, extraction);
  }

  updateExtraction(extraction: JSonExtraction): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/update`, extraction);
  }

  deleteExtraction(id: string): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/delete/${id}`);
  }

  launchExtraction(launchParams: JSonLaunchExtraction): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/launch`, launchParams);
  }
}
