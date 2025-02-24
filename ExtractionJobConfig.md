package com.mycompany.extraction.batch.config;

import com.mycompany.extraction.batch.tasklet.*;
import org.springframework.context.annotation.*;
import org.springframework.batch.core.*;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.batch.core.repository.JobRepository;

@Configuration
public class ExtractionJobConfig {

    @Autowired
    private JobRepository jobRepository;

    @Bean
    public ParseParametersTasklet parseParametersTasklet() {
        return new ParseParametersTasklet();
    }

    @Bean
    public GetTokenTasklet getTokenTasklet() {
        return new GetTokenTasklet();
    }

    @Bean
    public CallExtractionApiTasklet callExtractionApiTasklet() {
        return new CallExtractionApiTasklet();
    }

    // Steps
    @Bean
    public Step parseParametersStep(ParseParametersTasklet tasklet) {
        return new StepBuilder("parseParametersStep", jobRepository)
                .tasklet(tasklet)
                .build();
    }

    @Bean
    public Step getTokenStep(GetTokenTasklet tasklet) {
        return new StepBuilder("getTokenStep", jobRepository)
                .tasklet(tasklet)
                .build();
    }

    @Bean
    public Step callApiStep(CallExtractionApiTasklet tasklet) {
        return new StepBuilder("callApiStep", jobRepository)
                .tasklet(tasklet)
                .build();
    }

    /**
     * Le job => 3 steps
     */
    @Bean
    public Job extractionJob(Step parseParametersStep,
                             Step getTokenStep,
                             Step callApiStep) {
        return new JobBuilder("extractionJob", jobRepository)
                .start(parseParametersStep)
                .next(getTokenStep)
                .next(callApiStep)
                .build();
    }
}
