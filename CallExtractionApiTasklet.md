package com.mycompany.extraction.batch;

import org.springframework.batch.core.*;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Component
public class CallExtractionApiTasklet implements Tasklet {

    private final RestTemplate restTemplate = new RestTemplate();
    private final String extractionApiUrl = "http://localhost:8080/api/extraction/launch";

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
        ExecutionContext jobContext = chunkContext.getStepContext()
                .getStepExecution().getJobExecution().getExecutionContext();

        String token = (String) jobContext.get("accessToken");

        // On récupère l'objet JSonLaunchExtraction
        JSonLaunchExtraction launchObj = (JSonLaunchExtraction) jobContext.get("launchExtraction");
        if (launchObj == null) {
            throw new RuntimeException("No launchExtraction object found in jobContext!");
        }

        // On prépare le header
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<JSonLaunchExtraction> request = new HttpEntity<>(launchObj, headers);

        ResponseEntity<String> resp = restTemplate.exchange(
                extractionApiUrl,
                HttpMethod.POST,
                request,
                String.class
        );

        if (resp.getStatusCode().is2xxSuccessful()) {
            System.out.println("Extraction API launched successfully: " + resp.getBody());
        } else {
            throw new RuntimeException("Failed to launch extraction. Status=" + resp.getStatusCode());
        }

        return RepeatStatus.FINISHED;
    }
}
