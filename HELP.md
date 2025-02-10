@Test
void testMapJSonExtractionToSFCMExtractionEntity_withCellStyle() {
// On construit un JSonExtractionSheet avec un header ayant un cell style
JSonExtractionSheet sheet = new JSonExtractionSheet();
sheet.setExtractionSheetId(BigInteger.valueOf(101));

    JSonExtractionSheetHeader header = new JSonExtractionSheetHeader();
    header.setExtractionSheetHeaderId(BigInteger.valueOf(201));
    header.setHeaderName("Header1");

    JSonExtractionCellStyle style = new JSonExtractionCellStyle();
    style.setExtractionCellStyleId(BigInteger.valueOf(301));
    style.setCellStyle("BOLD");
    style.setBackgroundColor("GREEN");
    header.setJsonExtractionCellStyle(style);

    Set<JSonExtractionSheetHeader> headers = new HashSet<>();
    headers.add(header);
    sheet.setJsonExtractionSheetHeader(headers);

    Set<JSonExtractionSheet> sheets = new HashSet<>();
    sheets.add(sheet);

    JSonExtraction json = new JSonExtraction();
    json.setExtractionType("xls");
    json.setJsonExtractionSheet(sheets);

    // Appel du mapper
    SFCMExtractionEntity entity = mapper.mapJSonExtractionToSFCMExtractionEntity(json);

    // Vérif
    assertNotNull(entity);
    Set<SFCMExtractionSheetEntity> sheetEntities = entity.getExtractionSheetEntitys();
    assertNotNull(sheetEntities);
    assertEquals(1, sheetEntities.size());

    SFCMExtractionSheetEntity sheetEntity = sheetEntities.iterator().next();
    Set<SFCMExtractionSheetHeaderEntity> headerEntities = sheetEntity.getExtractionSheetHeaderEntitys();
    assertNotNull(headerEntities);
    assertEquals(1, headerEntities.size());

    SFCMExtractionSheetHeaderEntity headerEntity = headerEntities.iterator().next();
    SFCMExtractionCellStyleEntity styleEntity = headerEntity.getExtractionCellStyleEntity();
    assertNotNull(styleEntity);
    assertEquals(BigInteger.valueOf(301), styleEntity.getExtractionCellStyleId());
    assertEquals("BOLD", styleEntity.getCellStyle());
    assertEquals("GREEN", styleEntity.getBackgroundColor());
}
