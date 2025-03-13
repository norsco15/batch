package com.mycompany.extraction.batch;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.CommandLineRunner;
import org.springframework.batch.core.*;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.beans.factory.annotation.Autowired;

import com.mycompany.extraction.batch.util.JobParametersUtil;

@SpringBootApplication
public class ExtractionBatchApplication implements CommandLineRunner {

    @Autowired
    private JobLauncher jobLauncher;  // Injecté par Spring Boot
    @Autowired
    private Job extractionJob;        // Déclaré dans ExtractionJobConfig

    public static void main(String[] args) {
        SpringApplication.run(ExtractionBatchApplication.class, args);
    }

    @Override
    public void run(String... args) throws Exception {
        // 1) Construire jobParameters via la classe util
        JobParameters jobParams = JobParametersUtil.createJobParameters(args);

        // 2) Lancer le job
        JobExecution exec = jobLauncher.run(extractionJob, jobParams);
        System.out.println("Job ended => " + exec.getStatus());
    }
}
