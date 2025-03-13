package com.mycompany.extraction.batch.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Bean;
import org.springframework.beans.factory.annotation.Autowired;

import org.springframework.batch.core.*;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.transaction.PlatformTransactionManager;

import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.core.job.builder.JobBuilder;

import com.mycompany.extraction.batch.tasklet.*;

@Configuration
public class ExtractionJobConfig {

    @Autowired
    private JobRepository jobRepository;

    @Autowired
    private PlatformTransactionManager transactionManager;

    @Autowired
    private ParseParametersTasklet parseParametersTasklet;
    @Autowired
    private FindExtractionIdByNameTasklet findExtractionIdByNameTasklet;
    @Autowired
    private GetTokenTasklet getTokenTasklet;
    @Autowired
    private CallExtractionApiTasklet callExtractionApiTasklet;

    @Bean
    public Step parseStep() {
        return new StepBuilder("parseParametersStep", jobRepository)
                .tasklet(parseParametersTasklet, transactionManager) // + transactionManager
                .build();
    }

    @Bean
    public Step findStep() {
        return new StepBuilder("findExtractionIdByNameStep", jobRepository)
                .tasklet(findExtractionIdByNameTasklet, transactionManager) // + transactionManager
                .build();
    }

    @Bean
    public Step tokenStep() {
        return new StepBuilder("getTokenStep", jobRepository)
                .tasklet(getTokenTasklet, transactionManager) // + transactionManager
                .build();
    }

    @Bean
    public Step callStep() {
        return new StepBuilder("callExtractionApiStep", jobRepository)
                .tasklet(callExtractionApiTasklet, transactionManager) // + transactionManager
                .build();
    }

    @Bean
    public Job extractionJob(Step parseStep, Step findStep, Step tokenStep, Step callStep) {
        return new JobBuilder("extractionJob", jobRepository)
                .start(parseStep)
                .next(findStep)
                .next(tokenStep)
                .next(callStep)
                .build();
    }
}
