package com.mycompany.extraction.batch.tasklet;

import com.mycompany.extraction.batch.model.JSonLaunchExtraction;
import org.springframework.batch.core.*;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;

public class CallExtractionApiTasklet implements Tasklet {

    @Value("${extraction.api.url}")
    private String extractionApiUrl;

    private RestTemplate restTemplate = new RestTemplate();

    @Override
    public RepeatStatus execute(StepContribution contribution,
                                ChunkContext chunkContext) throws Exception {

        ExecutionContext ctx = chunkContext.getStepContext()
                .getStepExecution().getJobExecution().getExecutionContext();

        String token = (String) ctx.get("accessToken");
        if (token == null) {
            throw new RuntimeException("No token found in context!");
        }

        JSonLaunchExtraction launchObj = 
            (JSonLaunchExtraction) ctx.get("launchExtraction");
        if (launchObj == null) {
            throw new RuntimeException("No launchExtraction object found!");
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<JSonLaunchExtraction> request = new HttpEntity<>(launchObj, headers);

        // POST /api/extraction/launch
        ResponseEntity<String> resp = restTemplate.exchange(
                extractionApiUrl,
                HttpMethod.POST,
                request,
                String.class
        );

        if (resp.getStatusCode().is2xxSuccessful()) {
            System.out.println("Extraction launch success => " + resp.getBody());
        } else {
            throw new RuntimeException("Extraction launch failed => " + resp.getStatusCode());
        }

        return RepeatStatus.FINISHED;
    }
}
