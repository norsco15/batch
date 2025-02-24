package com.mycompany.extraction.batch;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class MainBatchLauncher {

    public static void main(String[] args) {
        // 1) Créer le contexte Spring
        AnnotationConfigApplicationContext context =
                new AnnotationConfigApplicationContext(BatchConfig.class);

        // 2) Récupérer le JobLauncher et le Job
        JobLauncher jobLauncher = context.getBean(JobLauncher.class);
        Job extractionJob = context.getBean("extractionJob", Job.class);

        try {
            // 3) Lancer le job
            JobExecution execution = jobLauncher.run(extractionJob, 
                    BatchConfig.createJobParametersFromSystemProperties(args));

            System.out.println("JobExecution finished with status: " + execution.getStatus());

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
