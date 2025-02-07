
class SCMExtractionControllerTest {

    @Mock
    private SCMExtractionService service;

    @InjectMocks
    private SCMExtractionController controller;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testSave() {
        JSonExtraction jsonExtraction = new JSonExtraction();
        jsonExtraction.setExtractionId(BigInteger.ONE);

        when(service.save(any(JSonExtraction.class))).thenReturn(jsonExtraction);

        JSonExtraction response = controller.save(jsonExtraction);

        assertNotNull(response);
        assertEquals(BigInteger.ONE, response.getExtractionId());
    }

    @Test
    void testLoadAll() {
        JSonExtraction extraction1 = new JSonExtraction();
        JSonExtraction extraction2 = new JSonExtraction();

        when(service.loadAll()).thenReturn(List.of(extraction1, extraction2));

        List<JSonExtraction> result = controller.loadAll();

        assertEquals(2, result.size());
    }

    @Test
    void testLoadOne() {
        JSonExtraction jsonExtraction = new JSonExtraction();
        jsonExtraction.setExtractionId(BigInteger.ONE);

        when(service.loadOne(BigInteger.ONE)).thenReturn(jsonExtraction);

        JSonExtraction result = controller.load_one(BigInteger.ONE);

        assertNotNull(result);
        assertEquals(BigInteger.ONE, result.getExtractionId());
    }

    @Test
    void testUpdate() {
        JSonExtraction jsonExtraction = new JSonExtraction();
        jsonExtraction.setExtractionId(BigInteger.ONE);

        when(service.update(any(JSonExtraction.class))).thenReturn(jsonExtraction);

        JSonExtraction result = controller.update(jsonExtraction);

        assertNotNull(result);
        assertEquals(BigInteger.ONE, result.getExtractionId());
    }

    @Test
    void testDelete() {
        ResponseEntity<String> response = controller.delete("1");

        assertEquals("Delete successfully!", response.getBody());
        verify(service, times(1)).delete(new BigInteger("1"));
    }

    @Test
    void testLaunch() {
        JSonLaunchExtraction launchExtraction = new JSonLaunchExtraction();
        launchExtraction.setExtractionId(BigInteger.ONE);

        ResponseEntity<String> response = controller.launch(launchExtraction);

        assertEquals("Batch Job launched successfully!", response.getBody());
        verify(service, times(1)).launch(launchExtraction);
    }
}

class SCMExtractionServiceTest {

    @Mock
    private SCMExtractionRepository repository;

    @InjectMocks
    private SCMExtractionService service;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testSave() {
        JSonExtraction jsonExtraction = new JSonExtraction();
        SCMExtractionEntity entity = new SCMExtractionEntity();
        when(repository.save(any(SCMExtractionEntity.class))).thenReturn(entity);

        JSonExtraction result = service.save(jsonExtraction);

        assertNotNull(result);
    }

    @Test
    void testLoadAll() {
        SCMExtractionEntity entity1 = new SCMExtractionEntity();
        SCMExtractionEntity entity2 = new SCMExtractionEntity();

        when(repository.findAll()).thenReturn(List.of(entity1, entity2));

        List<JSonExtraction> result = service.loadAll();

        assertEquals(2, result.size());
    }

    @Test
    void testLoadOne_Found() {
        SCMExtractionEntity entity = new SCMExtractionEntity();
        entity.setExtractionId(BigInteger.ONE);

        when(repository.findById(BigInteger.ONE)).thenReturn(Optional.of(entity));

        JSonExtraction result = service.loadOne(BigInteger.ONE);

        assertNotNull(result);
    }

    @Test
    void testLoadOne_NotFound() {
        when(repository.findById(BigInteger.ONE)).thenReturn(Optional.empty());

        assertThrows(RuntimeException.class, () -> service.loadOne(BigInteger.ONE));
    }

    @Test
    void testUpdate() {
        JSonExtraction jsonExtraction = new JSonExtraction();
        SCMExtractionEntity entity = new SCMExtractionEntity();

        when(repository.saveAndFlush(any(SCMExtractionEntity.class))).thenReturn(entity);

        JSonExtraction result = service.update(jsonExtraction);

        assertNotNull(result);
    }

    @Test
    void testDelete_Found() {
        when(repository.existsById(BigInteger.ONE)).thenReturn(true);

        assertDoesNotThrow(() -> service.delete(BigInteger.ONE));

        verify(repository, times(1)).deleteById(BigInteger.ONE);
    }

    @Test
    void testDelete_NotFound() {
        when(repository.existsById(BigInteger.ONE)).thenReturn(false);

        assertThrows(RuntimeException.class, () -> service.delete(BigInteger.ONE));
    }
}