package com.mycompany.extraction.batch.tasklet;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import org.junit.jupiter.api.Test;
import org.springframework.batch.core.*;
import org.springframework.batch.test.MetaDataInstanceFactory;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.batch.item.ExecutionContext;
import org.springframework.jdbc.core.JdbcTemplate;

public class FindExtractionIdByNameTaskletTest {

    @Test
    void testExecuteWithName() throws Exception {
        // GIVEN
        JdbcTemplate mockJdbc = mock(JdbcTemplate.class);
        FindExtractionIdByNameTasklet tasklet = new FindExtractionIdByNameTasklet();
        // on injecte le mock
        tasklet.setJdbcTemplate(mockJdbc);

        // Suppose qu'on va trouver l'ID = 123
        when(mockJdbc.queryForObject(
            eq("SELECT extraction_id FROM USR_EXTRACTION WHERE extraction_name = ?"),
            any(Object[].class),
            eq(Long.class)
        )).thenReturn(123L);

        // JobParameters => extractionName=MY_EXTRACT
        JobParameters params = new JobParametersBuilder()
            .addString("extractionName", "MY_EXTRACT")
            .toJobParameters();

        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(params);
        StepContribution contribution = stepExecution.createStepContribution();
        ChunkContext chunkContext = new ChunkContext(stepExecution);

        // On n'a pas d'extractionId -> normal
        ExecutionContext ctx = stepExecution.getJobExecution().getExecutionContext();
        assertNull(ctx.get("extractionId"));

        // WHEN
        RepeatStatus status = tasklet.execute(contribution, chunkContext);

        // THEN
        assertEquals(RepeatStatus.FINISHED, status);
        assertEquals("123", ctx.get("extractionId").toString());
        // Verif que le mock a été appelé
        verify(mockJdbc).queryForObject(anyString(), any(Object[].class), eq(Long.class));
    }

    @Test
    void testExecuteSkipIfAlreadyHaveId() throws Exception {
        JdbcTemplate mockJdbc = mock(JdbcTemplate.class);
        FindExtractionIdByNameTasklet tasklet = new FindExtractionIdByNameTasklet();
        tasklet.setJdbcTemplate(mockJdbc);

        // On suppose déjà extractionId=999 dans le context
        JobParameters params = new JobParametersBuilder()
            .addString("extractionId", "999")
            .toJobParameters();

        var stepExecution = MetaDataInstanceFactory.createStepExecution(params);
        var chunkContext = new ChunkContext(stepExecution);
        var contribution = stepExecution.createStepContribution();

        // WHEN
        RepeatStatus status = tasklet.execute(contribution, chunkContext);

        // THEN
        // on s'attend à ce qu'il skip la requête
        assertEquals(RepeatStatus.FINISHED, status);

        // on verifie que mockJdbc n'est pas appelé
        verifyNoInteractions(mockJdbc);
    }
}
