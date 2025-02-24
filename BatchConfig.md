package com.mycompany.extraction.batch.config;

import org.springframework.context.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;

import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.repository.support.JobRepositoryFactoryBean;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.launch.support.TaskExecutorJobLauncher;
import org.springframework.core.task.SyncTaskExecutor;

import org.springframework.batch.core.job.builder.JobParametersBuilder;
import org.springframework.batch.core.JobParameters;

import javax.sql.DataSource;
import java.util.Properties;

@Configuration
@EnableTransactionManagement
public class BatchInfraConfig {

    @Autowired
    private Environment env;

    /**
     * Créer un DataSource à partir de spring.datasource.*
     */
    @Bean
    public DataSource dataSource() {
        DriverManagerDataSource ds = new DriverManagerDataSource();
        ds.setUrl(env.getProperty("spring.datasource.url"));
        ds.setUsername(env.getProperty("spring.datasource.username"));
        ds.setPassword(env.getProperty("spring.datasource.password"));
        ds.setDriverClassName(env.getProperty("spring.datasource.driver-class-name"));
        return ds;
    }

    @Bean
    public PlatformTransactionManager transactionManager(DataSource ds) {
        return new DataSourceTransactionManager(ds);
    }

    /**
     * JobRepository stocké en DB => 
     * on utilise JobRepositoryFactoryBean + DataSource + TransactionManager.
     */
    @Bean
    public JobRepository jobRepository(DataSource ds, PlatformTransactionManager tm) throws Exception {
        JobRepositoryFactoryBean factory = new JobRepositoryFactoryBean();
        factory.setDataSource(ds);
        factory.setTransactionManager(tm);
        // factory.setTablePrefix("BATCH_");
        factory.afterPropertiesSet();
        return factory.getObject();
    }

    /**
     * TaskExecutorJobLauncher => Spring Batch 5
     * On évite SimpleJobLauncher (deprecated).
     */
    @Bean
    public JobLauncher jobLauncher(JobRepository jobRepository) throws Exception {
        TaskExecutorJobLauncher launcher = new TaskExecutorJobLauncher();
        launcher.setJobRepository(jobRepository);
        // Exec synchrone (un seul thread)
        launcher.setTaskExecutor(new SyncTaskExecutor());
        launcher.afterPropertiesSet();
        return launcher;
    }

    /**
     * Convertir arguments style --extractionId=123 => JobParameters
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
