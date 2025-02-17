<!-- attachFile -->
<mat-checkbox
  [checked]="extraction.jsonExtractionMail?.attachFile === 'Y'"
  (change)="extraction.jsonExtractionMail!.attachFile = $event.checked ? 'Y' : 'N'"
>
  Attach File?
</mat-checkbox>

<!-- zipFile -->
<mat-checkbox
  [checked]="extraction.jsonExtractionMail?.zipFile === 'Y'"
  (change)="extraction.jsonExtractionMail!.zipFile = $event.checked ? 'Y' : 'N'"
>
  Zip File?
</mat-checkbox>
