package com.mycompany.extraction.batch.tasklet;

import org.springframework.batch.core.*;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

public class GetTokenTasklet implements Tasklet {

    @Value("${keycloak.auth.url}")
    private String keycloakAuthUrl;

    @Value("${keycloak.client.id}")
    private String clientId;

    @Value("${keycloak.client.secret}")
    private String clientSecret;

    private RestTemplate restTemplate = new RestTemplate();

    @Override
    public RepeatStatus execute(StepContribution contribution,
                                ChunkContext chunkContext) throws Exception {

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        String body = "grant_type=client_credentials"
                + "&client_id=" + clientId
                + "&client_secret=" + clientSecret;

        HttpEntity<String> request = new HttpEntity<>(body, headers);

        ResponseEntity<Map> resp = restTemplate.postForEntity(keycloakAuthUrl, request, Map.class);

        if (resp.getStatusCode() == HttpStatus.OK && resp.getBody() != null) {
            Map map = resp.getBody();
            if (map.containsKey("access_token")) {
                String token = map.get("access_token").toString();

                ExecutionContext ctx = chunkContext.getStepContext()
                        .getStepExecution().getJobExecution().getExecutionContext();
                ctx.put("accessToken", token);

                System.out.println("Keycloak token => " 
                        + token.substring(0, Math.min(10, token.length())) + "...");
            } else {
                throw new RuntimeException("No access_token in response");
            }
        } else {
            throw new RuntimeException("Keycloak request failed => " + resp.getStatusCode());
        }

        return RepeatStatus.FINISHED;
    }
}
