package com.mycompany.extraction.batch.config;

import org.springframework.batch.core.*;
import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.configuration.support.DefaultBatchConfiguration;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.launch.support.SimpleJobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.context.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import com.mycompany.extraction.batch.tasklet.*;

import java.util.Properties;

@Configuration
@EnableBatchProcessing
public class BatchConfig extends DefaultBatchConfiguration {

    @Autowired
    private Environment env;

    // On override jobLauncher
    @Bean
    @Override
    public JobLauncher jobLauncher(JobRepository jobRepository) throws Exception {
        SimpleJobLauncher launcher = new SimpleJobLauncher();
        launcher.setJobRepository(jobRepository);
        launcher.afterPropertiesSet();
        return launcher;
    }

    // Déclaration des tasklets
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
    public Step parseParametersStep(JobRepository jobRepository,
                                   ParseParametersTasklet tasklet) {
        return new StepBuilder("parseParametersStep", jobRepository)
                .tasklet(tasklet)
                .build();
    }

    @Bean
    public Step getTokenStep(JobRepository jobRepository,
                             GetTokenTasklet tasklet) {
        return new StepBuilder("getTokenStep", jobRepository)
                .tasklet(tasklet)
                .build();
    }

    @Bean
    public Step callApiStep(JobRepository jobRepository,
                            CallExtractionApiTasklet tasklet) {
        return new StepBuilder("callApiStep", jobRepository)
                .tasklet(tasklet)
                .build();
    }

    // Le job
    @Bean
    public Job extractionJob(JobRepository jobRepository,
                             Step parseParametersStep,
                             Step getTokenStep,
                             Step callApiStep) {
        return new JobBuilder("extractionJob", jobRepository)
                .start(parseParametersStep)
                .next(getTokenStep)
                .next(callApiStep)
                .build();
    }

    /**
     * Transforme des arguments du style --extractionId=123 en JobParameters
     */
    public static JobParameters createJobParameters(String[] args) {
        Properties props = new Properties();
        for (String arg: args) {
            if (arg.startsWith("--")) {
                String[] kv = arg.substring(2).split("=", 2);
                if (kv.length == 2) {
                    props.put(kv[0], kv[1]);
                }
            }
        }
        JobParametersBuilder builder = new JobParametersBuilder();
        for (String name: props.stringPropertyNames()) {
            builder.addString(name, props.getProperty(name));
        }
        return builder.toJobParameters();
    }
}
