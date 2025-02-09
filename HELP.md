@Test
void testLaunch_csv() throws Exception {
// 1) Prépare un JSonLaunchExtraction (paramètre d’entrée)
JSonLaunchExtraction params = new JSonLaunchExtraction();
params.setExtractionId(BigInteger.valueOf(123));

    // 2) Crée une entité "csv" assez complète
    SFCMExtractionEntity entity = new SFCMExtractionEntity();
    entity.setExtractionId(BigInteger.valueOf(123));
    entity.setExtractionName("TestExtractionCSV");
    entity.setExtractionType("csv");

    // On crée un CSVEntity factice
    SFCMExtractionCSVEntity csvEntity = new SFCMExtractionCSVEntity();
    csvEntity.setExtractionCSVId(BigInteger.valueOf(999));
    // Peut-être qu’on a besoin d’un extractionSQLEntity aussi
    SFCMExtractionSQLEntity sqlEntity = new SFCMExtractionSQLEntity();
    sqlEntity.setExtractionSQLId(BigInteger.valueOf(111));
    sqlEntity.setExtractionSQLQuery("SELECT * FROM table_csv");
    csvEntity.setExtractionSQLEntity(sqlEntity);

    // On rattache le CSVEntity à l’entité principale
    entity.setExtractionCSVEntity(csvEntity);

    // 3) On mock le repository.findById(...) pour qu’il renvoie cette entité
    when(repository.findById(BigInteger.valueOf(123))).thenReturn(Optional.of(entity));

    // On peut aussi mocker jobLauncher.run(...) si besoin
    // jobLauncher.run(...) -> un mock de JobExecution
    // etc.

    // 4) Appel de la méthode launch
    service.launch(params);

    // 5) Vérifications
    verify(repository, times(1)).findById(BigInteger.valueOf(123));
    verify(jobLauncher, times(1)).run(any(), any()); // on peut affiner
    // ...
}
@Test
void testLaunch_xls() throws Exception {
// 1) Prépare un JSonLaunchExtraction (paramètre d’entrée)
JSonLaunchExtraction params = new JSonLaunchExtraction();
params.setExtractionId(BigInteger.valueOf(124));

    // 2) Crée une entité "xls" assez complète
    SFCMExtractionEntity entity = new SFCMExtractionEntity();
    entity.setExtractionId(BigInteger.valueOf(124));
    entity.setExtractionName("TestExtractionXLS");
    entity.setExtractionType("xls");

    // Ajout d’au moins un sheet
    SFCMExtractionSheetEntity sheetEntity = new SFCMExtractionSheetEntity();
    sheetEntity.setExtractionSheetId(BigInteger.valueOf(1000));
    sheetEntity.setSheetName("MySheet");
    // Dans le code "XLS", vous appelez sheetEntity.getExtractionSQLEntity() 
    // => on doit le set si nécessaire :
    SFCMExtractionSQLEntity sqlEntity = new SFCMExtractionSQLEntity();
    sqlEntity.setExtractionSQLId(BigInteger.valueOf(111));
    sqlEntity.setExtractionSQLQuery("SELECT * FROM table_xls");
    sheetEntity.setExtractionSQLEntity(sqlEntity);

    // rattachez le sheet au set
    Set<SFCMExtractionSheetEntity> sheets = new HashSet<>();
    sheets.add(sheetEntity);
    entity.setExtractionSheetEntitys(sheets);

    when(repository.findById(BigInteger.valueOf(124))).thenReturn(Optional.of(entity));

    service.launch(params);

    // Vérifications
    verify(repository, times(1)).findById(BigInteger.valueOf(124));
    verify(jobLauncher, times(1)).run(any(), any());
}
