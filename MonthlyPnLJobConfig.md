package com.example.monthlypnl.config;

import com.example.monthlypnl.tasklet.MonthlyPnLTasklet;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.configuration.annotation.JobBuilderFactory;
import org.springframework.batch.core.configuration.annotation.StepBuilderFactory;

import org.springframework.batch.core.launch.support.RunIdIncrementer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableBatchProcessing
public class MonthlyPnLJobConfig {

    /**
     * Déclare un job "monthlyPnLJob" avec un seul step
     */
    @Bean
    public Job monthlyPnLJob(JobBuilderFactory jobBuilderFactory, Step monthlyPnLStep) {
        return jobBuilderFactory.get("monthlyPnLJob")
                .incrementer(new RunIdIncrementer())
                .flow(monthlyPnLStep)
                .end()
                .build();
    }

    /**
     * Step unique qui lance le Tasklet "MonthlyPnLTasklet"
     */
    @Bean
    public Step monthlyPnLStep(StepBuilderFactory stepBuilderFactory, MonthlyPnLTasklet tasklet) {
        return stepBuilderFactory.get("monthlyPnLStep")
                .tasklet(tasklet)
                .build();
    }
}
