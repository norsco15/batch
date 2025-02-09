import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import java.math.BigInteger;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.*;
import javax.sql.DataSource;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.batch.core.*;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.item.database.JdbcCursorItemReader;
import org.springframework.batch.item.file.FlatFileItemWriter;
import org.springframework.core.io.FileSystemResource;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.transaction.PlatformTransactionManager;

@ExtendWith(MockitoExtension.class)
class SFCMExtractionServiceTest {

    @Mock private SFCMExtractionRepository repository;
    @Mock private EntityToJSonExtractionMapper entityToJSonMapper;
    @Mock private JSonToEntityExtractionMapper jsonToEntityMapper;
    @Mock private JobLauncher jobLauncher;
    @Mock private JobRepository jobRepository;
    @Mock private PlatformTransactionManager transactionManager;
    @Mock private DataSource dataSource;
    @Mock private JavaMailSender mailSender;
    
    @InjectMocks
    private SFCMExtractionService service;

    private JSonExtraction testJsonExtraction;
    private SFCMExtractionEntity testEntity;
    private JSonLaunchExtraction launchParams;

    @BeforeEach
    void setUp() {
        testJsonExtraction = new JSonExtraction();
        testJsonExtraction.setExtractionId(BigInteger.ONE);
        testJsonExtraction.setExtractionName("Test Extraction");
        
        testEntity = new SFCMExtractionEntity();
        testEntity.setExtractionId(BigInteger.ONE);
        testEntity.setExtractionType("csv");
        
        launchParams = new JSonLaunchExtraction();
        launchParams.setExtractionId(BigInteger.ONE);
    }

    // Tests pour save()
    @Test
    void save_ShouldMapAndPersistEntity() {
        when(jsonToEntityMapper.mapJSonExtractionToSFCMExtractionEntity(testJsonExtraction)).thenReturn(testEntity);
        when(repository.save(testEntity)).thenReturn(testEntity);
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(testEntity)).thenReturn(testJsonExtraction);

        JSonExtraction result = service.save(testJsonExtraction);
        
        verify(jsonToEntityMapper).mapJSonExtractionToSFCMExtractionEntity(testJsonExtraction);
        verify(repository).save(testEntity);
        verify(entityToJSonMapper).mapSFCMExtractionEntityToJSonExtraction(testEntity);
        assertEquals(testJsonExtraction.getExtractionId(), result.getExtractionId());
    }

    @Test
    void save_ShouldHandleNullInputGracefully() {
        assertThrows(NullPointerException.class, () -> service.save(null));
    }

    // Tests pour update()
    @Test
    void update_ShouldUpdateExistingEntity() {
        when(jsonToEntityMapper.mapJSonExtractionToSFCMExtractionEntity(testJsonExtraction)).thenReturn(testEntity);
        when(repository.saveAndFlush(testEntity)).thenReturn(testEntity);
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(testEntity)).thenReturn(testJsonExtraction);

        JSonExtraction result = service.update(testJsonExtraction);
        
        verify(repository).saveAndFlush(testEntity);
        assertEquals(testJsonExtraction.getExtractionName(), result.getExtractionName());
    }

    @Test
    void update_WithNonPersistedEntity_ShouldThrowException() {
        when(jsonToEntityMapper.mapJSonExtractionToSFCMExtractionEntity(any())).thenReturn(testEntity);
        when(repository.saveAndFlush(any())).thenThrow(new RuntimeException("Database error"));

        assertThrows(RuntimeException.class, () -> service.update(testJsonExtraction));
    }

    // Tests pour loadAll()
    @Test
    void loadAll_ShouldReturnAllEntities() {
        List<SFCMExtractionEntity> entities = Arrays.asList(testEntity, new SFCMExtractionEntity());
        when(repository.findAll()).thenReturn(entities);
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(any())).thenReturn(testJsonExtraction);

        List<JSonExtraction> result = service.loadAll();
        
        assertEquals(2, result.size());
        verify(repository).findAll();
    }

    @Test
    void loadAll_WithEmptyDatabase_ShouldReturnEmptyList() {
        when(repository.findAll()).thenReturn(Collections.emptyList());

        List<JSonExtraction> result = service.loadAll();
        
        assertTrue(result.isEmpty());
    }

    // Tests pour loadOne()
    @Test
    void loadOne_WithValidId_ShouldReturnEntity() {
        when(repository.findById(BigInteger.ONE)).thenReturn(testEntity);
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(testEntity)).thenReturn(testJsonExtraction);

        JSonExtraction result = service.loadOne(BigInteger.ONE);
        
        assertEquals(testJsonExtraction.getExtractionId(), result.getExtractionId());
    }

    @Test
    void loadOne_WithInvalidId_ShouldThrowException() {
        when(repository.findById(BigInteger.TEN)).thenReturn(null);

        assertThrows(NullPointerException.class, () -> service.loadOne(BigInteger.TEN));
    }

    // Tests pour delete()
    @Test
    void delete_WithExistingId_ShouldRemoveEntity() {
        when(repository.existsById(BigInteger.ONE)).thenReturn(true);
        
        service.delete(BigInteger.ONE);
        
        verify(repository).deleteById(BigInteger.ONE);
    }

    @Test
    void delete_WithNonExistingId_ShouldThrowDetailedException() {
        when(repository.existsById(BigInteger.TEN)).thenReturn(false);
        
        Exception exception = assertThrows(RuntimeException.class, 
            () -> service.delete(BigInteger.TEN));
        
        assertTrue(exception.getMessage().contains("not found"));
    }

    // Tests pour launch()
    @Test
    void launch_WithCsvType_ShouldExecuteCsvJob() throws Exception {
        when(repository.findById(BigInteger.ONE)).thenReturn(testEntity);
        when(jobLauncher.run(any(Job.class), any(JobParameters.class))).thenReturn(mock(JobExecution.class));

        service.launch(launchParams);
        
        ArgumentCaptor<Job> jobCaptor = ArgumentCaptor.forClass(Job.class);
        verify(jobLauncher).run(jobCaptor.capture(), any());
        
        assertTrue(jobCaptor.getValue().getName().startsWith("csvJob_"));
    }

    @Test
    void launch_WithXlsType_ShouldExecuteXlsJob() throws Exception {
        testEntity.setExtractionType("xls");
        when(repository.findById(BigInteger.ONE)).thenReturn(testEntity);
        when(jobLauncher.run(any(Job.class), any(JobParameters.class))).thenReturn(mock(JobExecution.class));

        service.launch(launchParams);
        
        verify(jobLauncher).run(any(Job.class), any(JobParameters.class));
    }

    @Test
    void launch_WithInvalidExtractionType_ShouldThrowException() {
        testEntity.setExtractionType("invalid");
        when(repository.findById(BigInteger.ONE)).thenReturn(testEntity);

        assertThrows(IllegalArgumentException.class, 
            () -> service.launch(launchParams));
    }

    // Tests pour les méthodes helper
    @Test
    void getQueryWithParameters_ShouldReplaceMultipleParameters() {
        SFCMExtractionSQLEntity sqlEntity = new SFCMExtractionSQLEntity();
        sqlEntity.setExtractionSQLQuery("SELECT :param1, :param2");
        
        Set<JSonExtractionParameters> params = new HashSet<>();
        params.add(new JSonExtractionParameters("param1", "value1"));
        params.add(new JSonExtractionParameters("param2", "value2"));

        when(jsonToEntityMapper.mapJsonExtractionParametersToMapParameters(params))
            .thenReturn(Map.of("param1", "value1", "param2", "value2"));

        String result = service.getQueryWithParameters(sqlEntity, params);
        
        assertEquals("SELECT value1, value2", result);
    }

    @Test
    void getDateFormatter_WithNullFormat_ShouldUseDefault() {
        SimpleDateFormat formatter = service.getDateFormatter(null);
        assertEquals("yyyyMMdd", formatter.toPattern());
    }

    @Test
    void getDecimalFormatter_WithCustomFormat_ShouldApplyFormat() {
        DecimalFormat formatter = service.getDecimalFormatter("#,##0.00");
        assertEquals("#,##0.00", formatter.toPattern());
    }

    @Test
    void dynamicRowMapper_ShouldHandleNullValues() throws SQLException {
        DynamicRowMapper mapper = new DynamicRowMapper();
        ResultSet rs = mock(ResultSet.class);
        ResultSetMetaData metaData = mock(ResultSetMetaData.class);
        
        when(rs.getMetaData()).thenReturn(metaData);
        when(metaData.getColumnCount()).thenReturn(1);
        when(metaData.getColumnName(1)).thenReturn("nullableColumn");
        when(rs.getObject(1)).thenReturn(null);

        Map<String, Object> result = mapper.mapRow(rs, 0);
        
        assertNull(result.get("nullableColumn"));
    }

    @Test
    void csvWriter_ShouldHandleMissingHeader() {
        SFCMExtractionCSVEntity csvConfig = new SFCMExtractionCSVEntity();
        csvConfig.setExtractionCSVSeparator(",");
        testEntity.setExtractionCSVEntity(csvConfig);

        FlatFileItemWriter<Map<String, Object>> writer = service.csvWriter(testEntity);
        
        assertNotNull(writer);
        assertDoesNotThrow(() -> writer.afterPropertiesSet());
    }

    @Test
    void createStepForSheet_ShouldBuildValidStep() {
        SFCMExtractionSheetEntity sheet = new SFCMExtractionSheetEntity();
        sheet.setSheetName("Test Sheet");
        
        Step step = service.createStepForSheet(sheet, Collections.emptySet());
        
        assertNotNull(step);
        assertEquals("Test Sheet", step.getName());
    }

    @Test
    void buildXlsJob_ShouldCreateMultiStepJob() {
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionName("MultiSheet");
        entity.setExtractionSheetEntitys(Set.of(
            new SFCMExtractionSheetEntity(),
            new SFCMExtractionSheetEntity()
        ));

        SFCMExtractionService serviceSpy = spy(service);
        doReturn(mock(Step.class)).when(serviceSpy).createStepForSheet(any(), any());

        Job job = serviceSpy.buildsJob(entity, Collections.emptySet());
        
        assertNotNull(job);
        verify(serviceSpy, times(2)).createStepForSheet(any(), any());
    }
}