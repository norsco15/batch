package com.mycompany.extraction.tasklet;

import com.mycompany.extraction.s3.S3BucketClient;
import com.mycompany.extraction.entity.SFCMExtractionEntity;
import lombok.extern.slf4j.Slf4j;
import org.apache.poi.ss.usermodel.Workbook;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.batch.core.step.tasklet.Tasklet;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;

@Slf4j
public class UploadXlsToS3Tasklet implements Tasklet {

    private final Workbook workbook;
    private final S3BucketClient s3Client;
    private final SFCMExtractionEntity extractionEntity;

    public UploadXlsToS3Tasklet(Workbook workbook,
                                S3BucketClient s3Client,
                                SFCMExtractionEntity extractionEntity) {
        this.workbook = workbook;
        this.s3Client = s3Client;
        this.extractionEntity = extractionEntity;
    }

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
        // On détermine par ex. bucketName, objectKey depuis extractionEntity
        // Suppose qu'il y a un xlsBucket, xlsObjectKey...
        String bucketName = extractionEntity.getExtractionCSVEntity().getS3BucketName();
        String objectKey = extractionEntity.getExtractionCSVEntity().getS3ObjectKeyXls(); 
        if (objectKey == null) {
            objectKey = "extractions/" + extractionEntity.getExtractionName() + ".xlsx";
        }

        log.info("[UploadXlsToS3Tasklet] => start uploading to s3://{}/{}", bucketName, objectKey);

        try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            // 1) Ecrire le workbook dans un flux mémoire
            workbook.write(baos);
            workbook.close(); // libérer mémoire

            byte[] data = baos.toByteArray();
            log.info("Workbook => {} bytes", data.length);

            // 2) putObject
            try (ByteArrayInputStream bais = new ByteArrayInputStream(data)) {
                s3Client.putObject(bucketName, objectKey, bais, data.length);
            }
            log.info("Upload XLS done => s3://{}/{}", bucketName, objectKey);

        } catch (Exception e) {
            log.error("Error uploading XLS => {}", e.getMessage(), e);
            throw e;
        }
        return RepeatStatus.FINISHED;
    }
}
