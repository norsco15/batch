@Test
void testMapSFCMExtractionEntityToJSonExtraction_withCellStyle() {
// Entité
SFCMExtractionEntity entity = new SFCMExtractionEntity();
entity.setExtractionType("xls");

    SFCMExtractionSheetEntity sheetEntity = new SFCMExtractionSheetEntity();
    sheetEntity.setExtractionSheetId(BigInteger.valueOf(101));

    SFCMExtractionSheetHeaderEntity headerEntity = new SFCMExtractionSheetHeaderEntity();
    headerEntity.setExtractionSheetHeaderId(BigInteger.valueOf(201));
    headerEntity.setHeaderName("Header1");

    // CellStyle
    SFCMExtractionCellStyleEntity styleEntity = new SFCMExtractionCellStyleEntity();
    styleEntity.setExtractionCellStyleId(BigInteger.valueOf(301));
    styleEntity.setCellStyle("BOLD");
    styleEntity.setBackgroundColor("GREEN");

    headerEntity.setExtractionCellStyleEntity(styleEntity);
    styleEntity.setExtractionSheetHeaderEntity(headerEntity);

    Set<SFCMExtractionSheetHeaderEntity> headers = new HashSet<>();
    headers.add(headerEntity);
    sheetEntity.setExtractionSheetHeaderEntitys(headers);

    Set<SFCMExtractionSheetEntity> sheets = new HashSet<>();
    sheets.add(sheetEntity);
    entity.setExtractionSheetEntitys(sheets);

    // Appel du mapper
    JSonExtraction json = mapper.mapSFCMExtractionEntityToJSonExtraction(entity);

    // Vérif
    assertNotNull(json);
    assertEquals("xls", json.getExtractionType());

    Set<JSonExtractionSheet> jsonSheets = json.getJsonExtractionSheet();
    assertNotNull(jsonSheets);
    assertEquals(1, jsonSheets.size());

    JSonExtractionSheet sheet = jsonSheets.iterator().next();
    Set<JSonExtractionSheetHeader> jsonHeaders = sheet.getJsonExtractionSheetHeader();
    assertNotNull(jsonHeaders);
    assertEquals(1, jsonHeaders.size());

    JSonExtractionSheetHeader header = jsonHeaders.iterator().next();
    JSonExtractionCellStyle style = header.getJsonExtractionCellStyle();
    assertNotNull(style);
    assertEquals(BigInteger.valueOf(301), style.getExtractionCellStyleId());
    assertEquals("BOLD", style.getCellStyle());
    assertEquals("GREEN", style.getBackgroundColor());
}
