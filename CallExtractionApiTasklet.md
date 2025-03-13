public class CallExtractionApiTaskletTest {

    @Test
    void testExecuteOk() throws Exception {
        RestTemplate mockRest = mock(RestTemplate.class);

        CallExtractionApiTasklet tasklet = new CallExtractionApiTasklet();
        tasklet.setRestTemplate(mockRest);
        tasklet.setExtractionApiUrl("http://localhost:8080/api/extraction/launch");

        // stepExecution => context with extractionId=123, accessToken=abc
        JobParameters params = new JobParametersBuilder().toJobParameters();
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(params);
        ExecutionContext ctx = stepExecution.getJobExecution().getExecutionContext();
        ctx.put("extractionId", new BigInteger("123"));
        ctx.put("accessToken", "abc");

        StepContribution contribution = stepExecution.createStepContribution();
        ChunkContext chunkContext = new ChunkContext(stepExecution);

        // Suppose reponse 200 OK
        ResponseEntity<String> response = new ResponseEntity<>("OK", HttpStatus.OK);
        when(mockRest.exchange(anyString(), eq(HttpMethod.POST), any(), eq(String.class)))
            .thenReturn(response);

        // WHEN
        RepeatStatus status = tasklet.execute(contribution, chunkContext);

        // THEN
        assertEquals(RepeatStatus.FINISHED, status);
        verify(mockRest).exchange(anyString(), eq(HttpMethod.POST), any(), eq(String.class));
    }
}
