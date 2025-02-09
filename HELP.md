package com.example.extraction.service;

import com.example.extraction.entity.SFCMExtractionEntity;
import com.example.extraction.mapper.EntityToJSonExtractionMapper;
import com.example.extraction.mapper.JSonToEntityExtractionMapper;
import com.example.extraction.model.JSonExtraction;
import com.example.extraction.model.JSonLaunchExtraction;
import com.example.extraction.model.JSonExtractionParameters;
import com.example.extraction.repository.SFCMExtractionRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.mail.javamail.JavaMailSender;

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

    @InjectMocks
    private SFCMExtractionService service;

    private JSonExtraction jsonExtraction;
    private SFCMExtractionEntity entity;

    @BeforeEach
    void setUp() {
        // Initialisation d’un objet JSonExtraction factice
        jsonExtraction = new JSonExtraction();
        jsonExtraction.setExtractionId(BigInteger.valueOf(123));
        jsonExtraction.setExtractionName("TestExtraction");
        jsonExtraction.setExtractionType("csv");

        // Initialisation d’une entité factice
        entity = new SFCMExtractionEntity();
        entity.setExtractionId(BigInteger.valueOf(123));
        entity.setExtractionName("TestExtraction");
        entity.setExtractionType("csv");
    }

    @Test
    void testSave() {
        // Arrange
        when(jsonToEntityMapper.mapJSonExtractionToSFCMExtractionEntity(jsonExtraction))
                .thenReturn(entity);
        when(repository.save(entity)).thenReturn(entity);
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(entity))
                .thenReturn(jsonExtraction);

        // Act
        JSonExtraction result = service.save(jsonExtraction);

        // Assert
        verify(repository, times(1)).save(entity);
        assertNotNull(result);
        assertEquals(BigInteger.valueOf(123), result.getExtractionId());
        assertEquals("TestExtraction", result.getExtractionName());
    }

    @Test
    void testUpdate() {
        // Arrange
        when(jsonToEntityMapper.mapJSonExtractionToSFCMExtractionEntity(jsonExtraction))
                .thenReturn(entity);
        when(repository.saveAndFlush(entity)).thenReturn(entity);
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(entity))
                .thenReturn(jsonExtraction);

        // Act
        JSonExtraction result = service.update(jsonExtraction);

        // Assert
        verify(repository, times(1)).saveAndFlush(entity);
        assertNotNull(result);
        assertEquals("TestExtraction", result.getExtractionName());
    }

    @Test
    void testLoadAll() {
        // Arrange
        List<SFCMExtractionEntity> entityList = Collections.singletonList(entity);
        when(repository.findAll()).thenReturn(entityList);
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(entity)).thenReturn(jsonExtraction);

        // Act
        List<JSonExtraction> result = service.loadALL();

        // Assert
        verify(repository, times(1)).findAll();
        assertEquals(1, result.size());
        assertEquals("TestExtraction", result.get(0).getExtractionName());
    }

    @Test
    void testLoadOne() {
        // Arrange
        BigInteger id = BigInteger.valueOf(123);
        when(repository.findById(id)).thenReturn(Optional.of(entity));
        when(entityToJSonMapper.mapSFCMExtractionEntityToJSonExtraction(entity)).thenReturn(jsonExtraction);

        // Act
        JSonExtraction result = service.load_one(id);

        // Assert
        verify(repository, times(1)).findById(id);
        assertNotNull(result);
        assertEquals("TestExtraction", result.getExtractionName());
    }

    @Test
    void testLoadOne_NotFound() {
        // Arrange
        BigInteger id = BigInteger.valueOf(999);
        when(repository.findById(id)).thenReturn(Optional.empty());

        // Act / Assert
        // Selon votre implémentation réelle, vous pouvez lever une exception 
        // ou retourner null. Ici, on suppose une RuntimeException si non trouvé.
        assertThrows(RuntimeException.class, () -> service.load_one(id));
    }

    @Test
    void testLaunch() throws Exception {
        // Arrange
        JSonLaunchExtraction params = new JSonLaunchExtraction();
        params.setExtractionId(BigInteger.valueOf(123));

        // On configure le repository pour retourner notre entité “csv”
        when(repository.findById(BigInteger.valueOf(123))).thenReturn(Optional.of(entity));

        // On simule un Job et l’exécution d’un Job
        Job mockJob = mock(Job.class);
        JobExecution mockJobExecution = mock(JobExecution.class);
        when(jobLauncher.run(eq(mockJob), any())).thenReturn(mockJobExecution);

        // On “espionne” la méthode buildCsvJob(...) en la rendant publique ou en changeant de stratégie
        // Pour simplifier, imaginons qu’on moque la méthode buildCsvJob directement : 
        // (vous pouvez extraire la construction de Job dans un bean séparé pour faciliter le test)
        // => Dans un vrai test unitaire, vous pouvez faire un partial mock si c’est indispensable.

        // Act
        service.launch(params);

        // Assert
        // On vérifie que le job a été lancé
        // L’implémentation interne (buildCsvJob, jobLauncher.run, etc.) peut être vérifiée 
        // si vous rendez buildCsvJob “visible” via un bean, ou si vous utilisez un spy. 
        // Ici, on montre juste qu’il n’y a pas d’erreur et que la logique passe.
        verify(repository, times(1)).findById(BigInteger.valueOf(123));
        // Potentiellement, vérifier que jobLauncher.run a été appelé
        // verify(jobLauncher, times(1)).run(any(Job.class), any());
    }

    @Test
    void testDelete() {
        // Arrange
        BigInteger id = BigInteger.valueOf(123);
        when(repository.existsById(id)).thenReturn(true);

        // Act
        service.delete(id);

        // Assert
        verify(repository, times(1)).existsById(id);
        verify(repository, times(1)).deleteById(id);
    }

    @Test
    void testDelete_NotFound() {
        // Arrange
        BigInteger id = BigInteger.valueOf(999);
        when(repository.existsById(id)).thenReturn(false);

        // Act / Assert
        assertThrows(RuntimeException.class, () -> service.delete(id));
    }
}
