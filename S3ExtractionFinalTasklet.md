public class S3ExtractionFinalTasklet implements Tasklet {

    private final SFCMExtractionEntity entity;
    private final S3BucketClient s3Client;
    // On reçoit EITHER the ByteArrayOutputStream for CSV OR the XSSFWorkbook for XLS (or both, but one is null)
    private final ByteArrayOutputStream csvOutput; 
    private final XSSFWorkbook workbook; 
    private final String extractionType; // to do the 'if'

    public S3ExtractionFinalTasklet(SFCMExtractionEntity entity,
                                    S3BucketClient s3Client,
                                    ByteArrayOutputStream csvOutput,
                                    XSSFWorkbook workbook,
                                    String extractionType) {
        this.entity = entity;
        this.s3Client = s3Client;
        this.csvOutput = csvOutput;
        this.workbook = workbook;
        this.extractionType = extractionType;
    }

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
        // 1) define bucket + objectKey
        String bucketName = "my-bucket"; // or from entity
        String objectKey;
        if ("csv".equalsIgnoreCase(extractionType)) {
            objectKey = entity.getExtractionName() + ".csv";
            // 2) read data from csvOutput
            byte[] data = csvOutput.toByteArray();
            try (ByteArrayInputStream bais = new ByteArrayInputStream(data)) {
                s3Client.putObject(bucketName, objectKey, bais, data.length, "text/csv");
            }
        } else if ("xls".equalsIgnoreCase(extractionType)) {
            objectKey = entity.getExtractionName() + ".xlsx";
            // 2) convert workbook => bytes
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            workbook.write(bos);
            workbook.close();
            byte[] data = bos.toByteArray();
            try (ByteArrayInputStream bais = new ByteArrayInputStream(data)) {
                s3Client.putObject(bucketName, objectKey, bais, data.length, 
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
            }
        }
        return RepeatStatus.FINISHED;
    }
}
