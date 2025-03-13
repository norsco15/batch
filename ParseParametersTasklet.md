package com.mycompany.extraction.batch.tasklet;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.test.MetaDataInstanceFactory;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.item.ExecutionContext;
import org.springframework.batch.repeat.RepeatStatus;

public class ParseParametersTaskletTest {

    @Test
    void testExecuteWithExtractionId() throws Exception {
        // GIVEN
        ParseParametersTasklet tasklet = new ParseParametersTasklet();

        // Simuler un jobParameters : --extractionId=123
        var jobParams = new JobParametersBuilder()
            .addString("extractionId", "123")
            .toJobParameters();

        // StepExecution factice
        var stepExecution = MetaDataInstanceFactory.createStepExecution(jobParams);
        StepContribution contribution = stepExecution.createStepContribution();
        ChunkContext chunkContext = new ChunkContext(stepExecution);

        // WHEN
        RepeatStatus status = tasklet.execute(contribution, chunkContext);

        // THEN
        assertEquals(RepeatStatus.FINISHED, status);

        ExecutionContext ctx = stepExecution.getJobExecution().getExecutionContext();
        assertNotNull(ctx.get("extractionId"));
        assertEquals("123", ctx.get("extractionId").toString());
        // On vérifie que l'ID a bien été stocké
    }

    @Test
    void testExecuteWithExtractionName() throws Exception {
        ParseParametersTasklet tasklet = new ParseParametersTasklet();

        var jobParams = new JobParametersBuilder()
            .addString("extractionName", "MY_EXTRACT")
            .toJobParameters();

        var stepExecution = MetaDataInstanceFactory.createStepExecution(jobParams);
        StepContribution contribution = stepExecution.createStepContribution();
        ChunkContext chunkContext = new ChunkContext(stepExecution);

        RepeatStatus status = tasklet.execute(contribution, chunkContext);
        assertEquals(RepeatStatus.FINISHED, status);

        ExecutionContext ctx = stepExecution.getJobExecution().getExecutionContext();
        assertEquals("MY_EXTRACT", ctx.get("extractionName"));
    }

    @Test
    void testExecuteNoIdNoName() throws Exception {
        ParseParametersTasklet tasklet = new ParseParametersTasklet();

        // pas d'ID ni de Name
        var jobParams = new JobParametersBuilder().toJobParameters();

        var stepExecution = MetaDataInstanceFactory.createStepExecution(jobParams);
        StepContribution contribution = stepExecution.createStepContribution();
        ChunkContext chunkContext = new ChunkContext(stepExecution);

        // On s'attend à une exception => "No extractionId nor extractionName provided!"
        assertThrows(RuntimeException.class, () -> {
            tasklet.execute(contribution, chunkContext);
        });
    }
}
