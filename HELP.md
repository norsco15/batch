
    @Mock
    private SCMExtractionRepository repository;

    @Mock
    private JSonToEntityExtractionMapper jsonToEntityMapper;

    @Mock
    private EntityToJSonExtractionMapper entityToJSonMapper;

    @Mock
    private JobLauncher jobLauncher;

    @Mock
    private JobRepository jobRepository;

    @Mock
    private PlatformTransactionManager transactionManager;

    @InjectMocks
    private SCMExtractionService service;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    /** ✅ Test de la méthode SAVE **/
    @Test
    void testSave_Success() {
        JSonExtraction jsonExtraction = createTestExtraction();
        SCMExtractionEntity entity = new SCMExtractionEntity();

        when(jsonToEntityMapper.mapJSonExtractionToSFCMExtractionEntity(any())).thenReturn(entity);
        when(repository.save(any())).thenReturn(entity);
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(any())).thenReturn(jsonExtraction);

        JSonExtraction result = service.save(jsonExtraction);

        assertNotNull(result);
        assertEquals(BigInteger.ONE, result.getExtractionId());
        assertEquals("Test Extraction", result.getExtractionName());
    }

    /** ✅ Test de la méthode LOAD_ALL **/
    @Test
    void testLoadAll_Success() {
        SCMExtractionEntity entity1 = new SCMExtractionEntity();
        SCMExtractionEntity entity2 = new SCMExtractionEntity();

        when(repository.findAll()).thenReturn(List.of(entity1, entity2));
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(any()))
                .thenReturn(new JSonExtraction(), new JSonExtraction());

        List<JSonExtraction> result = service.loadAll();

        assertEquals(2, result.size());
    }

    /** ✅ Test de la méthode LOAD_ONE **/
    @Test
    void testLoadOne_Success() {
        SCMExtractionEntity entity = new SCMExtractionEntity();
        entity.setExtractionId(BigInteger.ONE);
        entity.setExtractionName("Test Extraction");

        when(repository.findById(BigInteger.ONE)).thenReturn(Optional.of(entity));
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(any())).thenReturn(createTestExtraction());

        JSonExtraction result = service.loadOne(BigInteger.ONE);

        assertNotNull(result);
        assertEquals("Test Extraction", result.getExtractionName());
    }

    /** ✅ Test de la méthode LOAD_ONE avec ID inexistant **/
    @Test
    void testLoadOne_NotFound() {
        when(repository.findById(BigInteger.ONE)).thenReturn(Optional.empty());

        RuntimeException thrown = assertThrows(RuntimeException.class, () -> service.loadOne(BigInteger.ONE));
        assertEquals("Extraction not found", thrown.getMessage());
    }

    /** ✅ Test de la méthode UPDATE **/
    @Test
    void testUpdate_Success() {
        JSonExtraction jsonExtraction = createTestExtraction();
        SCMExtractionEntity entity = new SCMExtractionEntity();

        when(jsonToEntityMapper.mapJSonExtractionToSFCMExtractionEntity(any())).thenReturn(entity);
        when(repository.saveAndFlush(any())).thenReturn(entity);
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(any())).thenReturn(jsonExtraction);

        JSonExtraction result = service.update(jsonExtraction);

        assertNotNull(result);
        assertEquals("Test Extraction", result.getExtractionName());
    }

    /** ✅ Test de la méthode DELETE **/
    @Test
    void testDelete_Success() {
        when(repository.existsById(BigInteger.ONE)).thenReturn(true);
        doNothing().when(repository).deleteById(BigInteger.ONE);

        assertDoesNotThrow(() -> service.delete(BigInteger.ONE));
        verify(repository, times(1)).deleteById(BigInteger.ONE);
    }

    /** ✅ Test de la méthode DELETE avec ID inexistant **/
    @Test
    void testDelete_NotFound() {
        when(repository.existsById(BigInteger.ONE)).thenReturn(false);

        RuntimeException thrown = assertThrows(RuntimeException.class, () -> service.delete(BigInteger.ONE));
        assertEquals("Extraction not found", thrown.getMessage());
    }

    /** ✅ Test du lancement de l'extraction avec un format CSV **/
    @Test
    void testLaunchCsvJob_Success() throws Exception {
        JSonLaunchExtraction params = new JSonLaunchExtraction();
        params.setExtractionId(BigInteger.ONE);

        SCMExtractionEntity entity = new SCMExtractionEntity();
        entity.setExtractionType("csv");

        when(repository.findById(BigInteger.ONE)).thenReturn(Optional.of(entity));
        when(jobLauncher.run(any(), any())).thenReturn(mock(JobExecution.class));

        assertDoesNotThrow(() -> service.launch(params));
    }

    /** ✅ Test du lancement de l'extraction avec un format XLS **/
    @Test
    void testLaunchXlsJob_Success() throws Exception {
        JSonLaunchExtraction params = new JSonLaunchExtraction();
        params.setExtractionId(BigInteger.ONE);

        SCMExtractionEntity entity = new SCMExtractionEntity();
        entity.setExtractionType("xls");

        when(repository.findById(BigInteger.ONE)).thenReturn(Optional.of(entity));
        when(jobLauncher.run(any(), any())).thenReturn(mock(JobExecution.class));

        assertDoesNotThrow(() -> service.launch(params));
    }

    /** ✅ Test du lancement de l'extraction avec un format non supporté **/
    @Test
    void testLaunchUnsupportedFormat() {
        JSonLaunchExtraction params = new JSonLaunchExtraction();
        params.setExtractionId(BigInteger.ONE);

        SCMExtractionEntity entity = new SCMExtractionEntity();
        entity.setExtractionType("unsupported");

        when(repository.findById(BigInteger.ONE)).thenReturn(Optional.of(entity));

        IllegalArgumentException thrown = assertThrows(IllegalArgumentException.class, () -> service.launch(params));
        assertEquals("Unsupported extraction format: unsupported", thrown.getMessage());
    }