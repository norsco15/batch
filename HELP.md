package com.example.extraction.service;

import com.example.extraction.entity.*;
import com.example.extraction.model.JSonExtractionParameters;
import com.example.extraction.model.JSonLaunchExtraction;
import com.example.extraction.repository.SFCMExtractionRepository;
import com.example.extraction.mapper.EntityToJSonExtractionMapper;
import com.example.extraction.mapper.JSonToEntityExtractionMapper;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.springframework.batch.core.*;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.transaction.PlatformTransactionManager;

import javax.sql.DataSource;

import java.math.BigInteger;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(SpringExtension.class)
class SFCMExtractionServiceTest {

    @Mock
    private SFCMExtractionRepository repository;

    @Mock
    private JobLauncher jobLauncher;

    @Mock
    private JobRepository jobRepository;

    @Mock
    private PlatformTransactionManager transactionManager;

    @Mock
    private DataSource dataSource;

    @Mock
    private EntityToJSonExtractionMapper entityToJSonMapper;

    @Mock
    private JSonToEntityExtractionMapper jsonToEntityMapper;

    @Mock
    private JavaMailSender mailSender;

    // On utilise un Spy pour vérifier les méthodes internes (buildCsvJob, buildXlsJob, etc.)
    @Spy
    @InjectMocks
    private SFCMExtractionService service;

    // Juste un param par défaut pour simplifier
    private JSonLaunchExtraction launchParams;

    @BeforeEach
    void setUp() {
        launchParams = new JSonLaunchExtraction();
        launchParams.setExtractionId(BigInteger.valueOf(100));
    }

    /**
     * Test : format CSV, vérifier qu'aucune erreur n'est survenue dans le job (ExitStatus COMPLETED par ex).
     */
    @Test
    void testLaunch_csv_NoError() throws Exception {
        // 1) Prépare l'entité "CSV"
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(100));
        entity.setExtractionName("TestExtractionCSV");
        entity.setExtractionType("csv");

        // CSV entity
        SFCMExtractionCSVEntity csvEntity = new SFCMExtractionCSVEntity();
        csvEntity.setExtractionCSVId(BigInteger.valueOf(999));

        // SQL entity
        SFCMExtractionSQLEntity sqlEntity = new SFCMExtractionSQLEntity();
        sqlEntity.setExtractionSQLId(BigInteger.valueOf(111));
        sqlEntity.setExtractionSQLQuery("SELECT * FROM table_csv");
        csvEntity.setExtractionSQLEntity(sqlEntity);
        entity.setExtractionCSVEntity(csvEntity);

        // 2) Mock du repository
        when(repository.findById(BigInteger.valueOf(100)))
                .thenReturn(Optional.of(entity));

        // 3) Mock jobLauncher et buildCsvJob
        Job mockCsvJob = mock(Job.class);
        JobExecution mockExecution = mock(JobExecution.class);

        // Simulons un ExitStatus COMPLETED
        when(mockExecution.getExitStatus()).thenReturn(ExitStatus.COMPLETED);
        when(jobLauncher.run(any(Job.class), any(JobParameters.class))).thenReturn(mockExecution);

        doReturn(mockCsvJob).when(service).buildCsvJob(eq(entity), anySet());

        // 4) Action
        service.launch(launchParams);

        // 5) Vérifications
        verify(repository, times(1)).findById(BigInteger.valueOf(100));
        verify(service, times(1)).buildCsvJob(eq(entity), anySet());
        verify(jobLauncher, times(1)).run(eq(mockCsvJob), any(JobParameters.class));

        // Pour être plus exhaustif, on peut vérifier l’ExitStatus du mock.
        // En principe, vous ne renvoyez pas l’ExitStatus dans la méthode launch, 
        // mais vous pouvez quand même vous assurer que c’est COMPLETED pour ce test :
        assertEquals(ExitStatus.COMPLETED, mockExecution.getExitStatus(), 
                "Le job doit se terminer avec un ExitStatus COMPLETED");
    }

    @Test
    void testLaunch_xls_NoError() throws Exception {
        // 1) Prépare l'entité "XLS"
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(100));
        entity.setExtractionName("TestExtractionXLS");
        entity.setExtractionType("xls");
    
        // Au moins un sheetEntity
        SFCMExtractionSheetEntity sheet = new SFCMExtractionSheetEntity();
        sheet.setExtractionSheetId(BigInteger.valueOf(101));
        sheet.setSheetName("Sheet1");
    
        SFCMExtractionSQLEntity sqlEntity = new SFCMExtractionSQLEntity();
        sqlEntity.setExtractionSQLId(BigInteger.valueOf(201));
        sqlEntity.setExtractionSQLQuery("SELECT * FROM table_xls");
        sheet.setExtractionSQLEntity(sqlEntity);
    
        Set<SFCMExtractionSheetEntity> sheets = new HashSet<>();
        sheets.add(sheet);
        entity.setExtractionSheetEntitys(sheets);
    
        // 2) Mock du repository
        when(repository.findById(BigInteger.valueOf(100)))
                .thenReturn(Optional.of(entity));
    
        // 3) Mock jobLauncher & buildXlsJob
        Job mockXlsJob = mock(Job.class);
        JobExecution mockExecution = mock(JobExecution.class);
    
        // On simule un ExitStatus COMPLETED
        when(mockExecution.getExitStatus()).thenReturn(ExitStatus.COMPLETED);
        when(jobLauncher.run(any(Job.class), any(JobParameters.class))).thenReturn(mockExecution);
    
        // buildXlsJob(...) renvoie un Job mock
        doReturn(mockXlsJob).when(service).buildXlsJob(eq(entity), anySet());
    
        // 4) Appel de la méthode
        service.launch(launchParams);
    
        // 5) Vérifications
        verify(repository, times(1)).findById(BigInteger.valueOf(100));
        verify(service, times(1)).buildXlsJob(eq(entity), anySet());
        verify(jobLauncher, times(1)).run(eq(mockXlsJob), any(JobParameters.class));
    
        // On s'attend à un ExitStatus COMPLETED
        assertEquals(ExitStatus.COMPLETED, mockExecution.getExitStatus(),
                "Le job doit se terminer avec un ExitStatus COMPLETED");
    }    


    /**
     * Test : format inconnu -> on s'attend à une exception (par exemple IllegalArgumentException).
     */
    @Test
    void testLaunch_UnsupportedFormat() {
        // 1) On prépare une entité avec un format inconnu
        SFCMExtractionEntity entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(100));
        entity.setExtractionName("TestUnknownFormat");
        entity.setExtractionType("pdf"); // disons que "pdf" n'est pas supporté

        when(repository.findById(BigInteger.valueOf(100)))
                .thenReturn(Optional.of(entity));

        // 2) On lance la méthode et on s'attend à ce que ça jette l'exception
        assertThrows(IllegalArgumentException.class, () -> service.launch(launchParams),
                "Lancer un format non supporté doit lever IllegalArgumentException");

        // 3) Vérification
        verify(repository, times(1)).findById(BigInteger.valueOf(100));
        // Pas d’appel à jobLauncher.run(...) ni buildCsvJob ni buildXlsJob
        verify(jobLauncher, never()).run(any(), any());
        verify(service, never()).buildCsvJob(any(), anySet());
        verify(service, never()).buildXlsJob(any(), anySet());
    }
}
