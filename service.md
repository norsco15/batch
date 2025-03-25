@Bean
public ItemWriter<Map<String, Object>> s3CsvInMemoryWriter(S3BucketClient s3Client) {
    // Suppose que vous avez myService.buildLine(...) => on l'expose par un lambda
    S3CsvInMemoryWriter.BuildLineFunction buildFn = (item, sep) -> myService.buildLine(item, sep);

    return new S3CsvInMemoryWriter(
        s3Client,
        "my-bucket",
        "extractions/myOneShot.csv",
        "col1;col2;col3", // header
        ";",              // separator
        buildFn
    );
}

@Bean
public Step csvStep(JobRepository jobRepository,
                    PlatformTransactionManager transactionManager,
                    ItemReader<Map<String,Object>> reader,
                    ItemWriter<Map<String,Object>> s3CsvInMemoryWriter) {
    return new StepBuilder("csvStep", jobRepository)
        .<Map<String,Object>, Map<String,Object>>chunk(50, transactionManager)
        .reader(reader)
        .writer(s3CsvInMemoryWriter)
        .build();
}
