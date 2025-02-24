package com.mycompany.extraction.batch;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import com.mycompany.extraction.batch.config.BatchConfig;

public class MainBatchLauncher {

    public static void main(String[] args) {
        // 1) Créer un contexte Spring
        AnnotationConfigApplicationContext context =
                new AnnotationConfigApplicationContext(BatchConfig.class);

        // 2) Récupérer JobLauncher et Job
        JobLauncher jobLauncher = context.getBean(JobLauncher.class);
        Job extractionJob = context.getBean("extractionJob", Job.class);

        try {
            // 3) Construire JobParameters à partir des arguments (ex: --extractionId=123)
            var jobParams = BatchConfig.createJobParameters(args);

            // 4) Lancer
            JobExecution execution = jobLauncher.run(extractionJob, jobParams);
            System.out.println("Job finished with status: " + execution.getStatus());

        } catch (Exception e) {
            System.err.println("Failed to run job: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        } finally {
            context.close();
        }
        System.exit(0);
    }
}
