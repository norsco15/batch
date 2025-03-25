package com.mycompany.extraction.writer;

import com.mycompany.extraction.s3.S3BucketClient;
import lombok.extern.slf4j.Slf4j;
import org.springframework.batch.item.support.AbstractItemStreamItemWriter;
import org.springframework.batch.item.ExecutionContext;
import org.springframework.batch.item.Chunk;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.util.Map;

/**
 * ItemWriter qui accumule toutes les lignes CSV en mémoire (StringBuilder),
 * puis à la fermeture, fait un unique putObject sur S3.
 *
 * -> Pas de fichier local, juste un gros buffer en RAM.
 */
@Slf4j
public class S3CsvInMemoryWriter extends AbstractItemStreamItemWriter<Map<String, Object>> {

    // On suppose que vous avez déjà un s3Client
    private final S3BucketClient s3Client;
    private final String bucketName;
    private final String objectKey;

    // Paramètres pour CSV
    private final String header;
    private final String separator;

    // Interface fonctionnelle pour votre buildLine(...) custom
    private final BuildLineFunction buildLineFn;

    // Accumulateur en mémoire
    private StringBuilder buffer;

    public S3CsvInMemoryWriter(S3BucketClient s3Client,
                               String bucketName,
                               String objectKey,
                               String header,
                               String separator,
                               BuildLineFunction buildLineFn) {
        this.s3Client = s3Client;
        this.bucketName = bucketName;
        this.objectKey = objectKey;
        this.header = header;
        this.separator = separator;
        this.buildLineFn = buildLineFn;

        setExecutionContextName(this.getClass().getSimpleName());
    }

    @Override
    public void open(ExecutionContext executionContext) {
        super.open(executionContext);
        log.info("[S3CsvInMemoryWriter] open => init in-memory buffer");
        buffer = new StringBuilder();

        // Si besoin d'un header CSV
        if (header != null) {
            buffer.append(header).append("\n");
        }
    }

    @Override
    public void write(Chunk<? extends Map<String, Object>> chunk) throws Exception {
        for (Map<String, Object> item : chunk) {
            // On appelle votre logique existante
            String line = buildLineFn.buildLine(item, separator);
            buffer.append(line).append("\n");
        }
    }

    @Override
    public void close() {
        log.info("[S3CsvInMemoryWriter] close => putObject sur S3 en one shot");
        try {
            if (buffer == null || buffer.length() == 0) {
                log.warn("Buffer vide => aucun contenu à envoyer");
                super.close();
                return;
            }

            // Convertir en bytes
            byte[] data = buffer.toString().getBytes(StandardCharsets.UTF_8);
            ByteArrayInputStream bais = new ByteArrayInputStream(data);

            // putObject => on suppose que S3BucketClient a putObject(bucket, key, inputStream, length)
            s3Client.putObject(bucketName, objectKey, bais, data.length);

            log.info("Upload terminé => bucket={}, key={}, size={}", bucketName, objectKey, data.length);

        } catch (Exception e) {
            log.error("Erreur lors du putObject => {}", e.getMessage(), e);
            throw new RuntimeException("S3 upload failed", e);
        } finally {
            // libérer le buffer
            buffer = null;
            super.close();
        }
    }

    @FunctionalInterface
    public interface BuildLineFunction {
        String buildLine(Map<String, Object> item, String separator);
    }
}
