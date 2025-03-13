package com.mycompany.extraction.batch.tasklet;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import org.junit.jupiter.api.Test;
import org.springframework.batch.core.*;
import org.springframework.batch.test.MetaDataInstanceFactory;
import org.springframework.http.*;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.batch.item.ExecutionContext;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

public class GetTokenTaskletTest {

    @Test
    void testExecuteOk() throws Exception {
        // Mock RestTemplate
        RestTemplate mockRest = mock(RestTemplate.class);

        GetTokenTasklet tasklet = new GetTokenTasklet();
        // on injecte le mock
        tasklet.setRestTemplate(mockRest);
        // On définit les url, clientId, clientSecret si le code utilise
        tasklet.setKeycloakAuthUrl("https://my-keycloak.com/auth/realms/myrealm/protocol/openid-connect/token");
        tasklet.setClientId("myClientId");
        tasklet.setClientSecret("mySecret");

        // Suppose reponse 200 + body => { "access_token" : "abc123" }
        Map<String,String> body = Map.of("access_token","abc123");
        ResponseEntity<Map> response = new ResponseEntity<>(body, HttpStatus.OK);
        when(mockRest.postForEntity(anyString(), any(), eq(Map.class)))
            .thenReturn(response);

        // StepExecution
        JobParameters jobParams = new JobParametersBuilder().toJobParameters();
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParams);
        StepContribution contribution = stepExecution.createStepContribution();
        ChunkContext chunkContext = new ChunkContext(stepExecution);

        // WHEN
        RepeatStatus status = tasklet.execute(contribution, chunkContext);

        // THEN
        assertEquals(RepeatStatus.FINISHED, status);
        ExecutionContext ctx = stepExecution.getJobExecution().getExecutionContext();
        assertEquals("abc123", ctx.get("accessToken"));
    }

    @Test
    void testExecuteUnauthorized() throws Exception {
        // ...
        // On simule un 401 => HttpClientErrorException
        // On verifie qu'on catch la runtimeException ou qu'on fail
    }
}
