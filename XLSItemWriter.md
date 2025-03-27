package com.mycompany.batch.tasklet;

import com.mycompany.entity.SFCMExtractionEntity;
import com.mycompany.s3.S3BucketClient;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.batch.repeat.RepeatStatus;
import javax.mail.internet.MimeMessage;
// autres imports

public class EmailTasklet implements Tasklet {

    private final SFCMExtractionEntity entity;
    private final S3BucketClient s3Client;
    private final JavaMailSender mailSender;

    public EmailTasklet(SFCMExtractionEntity entity,
                        S3BucketClient s3Client,
                        JavaMailSender mailSender) {
        this.entity = entity;
        this.s3Client = s3Client;
        this.mailSender = mailSender;
    }

    @Override
    public RepeatStatus execute(StepContribution contrib, ChunkContext chunkCtx) throws Exception {
        if (!"Y".equalsIgnoreCase(entity.getExtractionMail())) {
            return RepeatStatus.FINISHED;
        }
        // ... code pour construire le MimeMessage, 
        //    télécharger object S3 (CSV ou XLS) et l'attacher,
        //    mailSender.send(...)
        return RepeatStatus.FINISHED;
    }
}


@Bean
public Step emailStep(JobRepository jobRepo,
                      PlatformTransactionManager txMgr,
                      SFCMExtractionEntity entity,
                      S3BucketClient s3Client,
                      JavaMailSender mailSender) {
    Tasklet tasklet = new EmailTasklet(entity, s3Client, mailSender);
    return new StepBuilder("emailStep", jobRepo)
        .tasklet(tasklet, txMgr)
        .build();
}
