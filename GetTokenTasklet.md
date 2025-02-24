package com.mycompany.extraction.batch;

import java.util.Map;
import org.springframework.batch.core.*;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class GetTokenTasklet implements Tasklet {

    private RestTemplate restTemplate = new RestTemplate();

    // Suppose vous avez un URL Keycloak, clientId, secret
    private String keycloakUrl = "https://my-keycloak/auth/realms/myrealm/protocol/openid-connect/token";
    private String clientId = "myclient";
    private String clientSecret = "mysecret";

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
        ExecutionContext jobContext = chunkContext.getStepContext()
                .getStepExecution()
                .getJobExecution()
                .getExecutionContext();

        // 1) On appelle Keycloak pour le token
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        String body = "grant_type=client_credentials"
                + "&client_id=" + clientId
                + "&client_secret=" + clientSecret;

        HttpEntity<String> request = new HttpEntity<>(body, headers);

        ResponseEntity<Map> response = restTemplate.postForEntity(keycloakUrl, request, Map.class);

        if (response.getStatusCode() == HttpStatus.OK && response.getBody().containsKey("access_token")) {
            String token = (String) response.getBody().get("access_token");
            System.out.println("Received token from Keycloak: " + token.substring(0, 10) + "...");
            jobContext.put("accessToken", token);
        } else {
            throw new RuntimeException("Failed to get token from Keycloak");
        }
        return RepeatStatus.FINISHED;
    }
}
