package com.mycompany.extraction.s3;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.InputStream;

@Slf4j
@Component
public class S3BucketClient {

    private final AmazonS3 s3;

    public S3BucketClient(AmazonS3 s3) {
        this.s3 = s3;
    }

    public void putObject(String bucketName, String objectKey, InputStream data, long contentLength) {
        try {
            ObjectMetadata meta = new ObjectMetadata();
            meta.setContentLength(contentLength);
            meta.setContentType("text/csv");

            PutObjectRequest req = new PutObjectRequest(bucketName, objectKey, data, meta);
            s3.putObject(req);

            log.info("S3 putObject => bucket={}, key={}, size={}", bucketName, objectKey, contentLength);
        } catch (Exception e) {
            log.error("Error putObject => {}", e.getMessage(), e);
            throw new RuntimeException("Failed S3 putObject", e);
        }
    }
}
