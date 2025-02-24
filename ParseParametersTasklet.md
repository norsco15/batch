package com.mycompany.extraction.batch;

import org.springframework.batch.core.*;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.stereotype.Component;

@Component
@StepScope
public class ParseParametersTasklet implements Tasklet {

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
        JobParameters jobParams = chunkContext.getStepContext()
                .getStepExecution()
                .getJobExecution()
                .getJobParameters();

        String extractionId = jobParams.getString("extractionId", "0");
        String paramList = jobParams.getString("paramList", ""); // ex: "ENV=PREPROD;TYPE=FULL"

        ExecutionContext jobContext = chunkContext.getStepContext()
                .getStepExecution()
                .getJobExecution()
                .getExecutionContext();

        // 1) Convertir extractionId en BigInteger
        BigInteger idBI = new BigInteger(extractionId);

        // 2) Parser paramList => Set<JSonExtractionParameters>
        Set<JSonExtractionParameters> paramSet = parseParamList(paramList);

        // 3) Construire l’objet JSonLaunchExtraction
        JSonLaunchExtraction launchObj = new JSonLaunchExtraction();
        launchObj.setExtractionId(idBI);
        launchObj.setExtractionParameters(paramSet);

        // 4) Stocker l’objet "launchObj" dans le jobContext
        jobContext.put("launchExtraction", launchObj);

        System.out.println("Parsed extractionId=" + extractionId + " paramList=" + paramList);
        System.out.println("launchObj=" + launchObj);

        return RepeatStatus.FINISHED;
    }

    private Set<JSonExtractionParameters> parseParamList(String paramList) {
        Set<JSonExtractionParameters> set = new HashSet<>();
        if (paramList == null || paramList.trim().isEmpty()) {
            return set;
        }
        // Suppose c’est "ENV=PREPROD;TYPE=FULL"
        String[] pairs = paramList.split(";");
        for (String pair : pairs) {
            String[] kv = pair.split("=", 2);
            if (kv.length == 2) {
                JSonExtractionParameters p = new JSonExtractionParameters();
                p.setParameterName(kv[0]);
                p.setParameterValue(kv[1]);
                set.add(p);
            }
        }
        return set;
    }
}
