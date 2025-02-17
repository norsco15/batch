ngOnInit(): void {
  // 1) Mode CREATE ou MODIFY
  if (this.router.url.includes('/update')) {
    this.formAction = 'MODIFY';

    // On récupère l'extraction depuis history.state
    const st: any = history.state;
    if (st) {
      // On assigne l'extraction
      this.extraction = st;

      // 2) Normaliser extractionMail ('Y' ou 'N')
      if (this.extraction.extractionMail) {
        // ex. 'y', 'Y', 'n', 'N' => on met 'Y' ou 'N'
        const mailVal = this.extraction.extractionMail.toUpperCase();
        this.extraction.extractionMail = (mailVal === 'Y') ? 'Y' : 'N';
      } else {
        // si undefined => 'N'
        this.extraction.extractionMail = 'N';
      }

      // 3) Normaliser extractionType (ex. 'csv' => 'CSV')
      if (this.extraction.extractionType) {
        this.extraction.extractionType = this.extraction.extractionType.toUpperCase();
      }

      // 4) Normaliser attachFile & zipFile (dans jsonExtractionMail) => 'Y' ou 'N'
      if (this.extraction.jsonExtractionMail) {
        // attachFile
        if (this.extraction.jsonExtractionMail.attachFile) {
          const val = this.extraction.jsonExtractionMail.attachFile.toUpperCase();
          this.extraction.jsonExtractionMail.attachFile = (val === 'Y') ? 'Y' : 'N';
        } else {
          this.extraction.jsonExtractionMail.attachFile = 'N';
        }

        // zipFile
        if (this.extraction.jsonExtractionMail.zipFile) {
          const val = this.extraction.jsonExtractionMail.zipFile.toUpperCase();
          this.extraction.jsonExtractionMail.zipFile = (val === 'Y') ? 'Y' : 'N';
        } else {
          this.extraction.jsonExtractionMail.zipFile = 'N';
        }
      }
    }
  } else {
    // Mode CREATE
    this.formAction = 'CREATE';
  }

  // Si extractionMail n'est pas défini => 'N'
  if (!this.extraction.extractionMail) {
    this.extraction.extractionMail = 'N';
  }

  // 5) Si on a déjà un extractionType => on (re)déclenche la logique CSV / XLS
  if (this.extraction.extractionType) {
    this.extraction.extractionType = this.extraction.extractionType.toUpperCase();
    this.onReportTypeChange();
  }
}
