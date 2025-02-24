package com.mycompany.extraction.batch.config;

import org.springframework.context.annotation.*;
import org.springframework.batch.core.repository.*;
import org.springframework.batch.core.repository.support.MapJobRepositoryFactoryBean;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.launch.support.TaskExecutorJobLauncher;
import org.springframework.core.task.SyncTaskExecutor;

import org.springframework.batch.core.job.builder.JobParametersBuilder;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;

import java.util.Properties;

@Configuration
@EnableBatchProcessing
public class BatchConfig {

    /**
     * Crée un JobRepository en mémoire (MapJobRepositoryFactoryBean).
     * => plus besoin de DataSource
     */
    @Bean
    public JobRepository jobRepository() throws Exception {
        MapJobRepositoryFactoryBean factory = new MapJobRepositoryFactoryBean();
        factory.afterPropertiesSet();
        return factory.getObject();
    }

    /**
     * TaskExecutorJobLauncher (non déprécié), s'appuie sur le jobRepository en mémoire.
     */
    @Bean
    public JobLauncher jobLauncher(JobRepository jobRepository) throws Exception {
        TaskExecutorJobLauncher launcher = new TaskExecutorJobLauncher();
        launcher.setJobRepository(jobRepository);
        // exécution synchrone (un seul thread)
        launcher.setTaskExecutor(new SyncTaskExecutor());
        launcher.afterPropertiesSet();
        return launcher;
    }

    /**
     * Convertir les arguments (ex: --extractionId=123) en JobParameters
     */
    public static JobParameters createJobParameters(String[] args) {
        Properties props = new Properties();
        for (String arg : args) {
            if (arg.startsWith("--")) {
                String[] kv = arg.substring(2).split("=", 2);
                if (kv.length == 2) {
                    props.put(kv[0], kv[1]);
                }
            }
        }
        JobParametersBuilder builder = new JobParametersBuilder();
        for (String name : props.stringPropertyNames()) {
            builder.addString(name, props.getProperty(name));
        }
        return builder.toJobParameters();
    }
}
