package com.mycompany.extraction.batch.tasklet;

import com.mycompany.extraction.batch.model.JSonExtractionParameters;
import com.mycompany.extraction.batch.model.JSonLaunchExtraction;
import org.springframework.batch.core.*;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;

import java.math.BigInteger;
import java.util.HashSet;
import java.util.Set;

public class ParseParametersTasklet implements Tasklet {

    @Override
    public RepeatStatus execute(StepContribution contribution,
                                ChunkContext chunkContext) throws Exception {
        JobParameters jobParams = chunkContext.getStepContext()
                .getStepExecution()
                .getJobExecution()
                .getJobParameters();

        // ex: --extractionId=123, --paramList="ENV=PREPROD;TYPE=FULL"
        String extractionIdStr = jobParams.getString("extractionId", "0");
        String paramList = jobParams.getString("paramList", "");

        // On construit l'objet
        JSonLaunchExtraction launchObj = new JSonLaunchExtraction();
        launchObj.setExtractionId(new BigInteger(extractionIdStr));
        launchObj.setExtractionParameters(parseParamList(paramList));

        ExecutionContext ctx = chunkContext.getStepContext()
                .getStepExecution().getJobExecution().getExecutionContext();
        ctx.put("launchExtraction", launchObj);

        System.out.println("ParseParameters => extractionId=" + extractionIdStr 
                + ", paramList=" + paramList);

        return RepeatStatus.FINISHED;
    }

    private Set<JSonExtractionParameters> parseParamList(String paramList) {
        Set<JSonExtractionParameters> set = new HashSet<>();
        if (paramList == null || paramList.trim().isEmpty()) {
            return set;
        }
        // Suppose "ENV=PREPROD;TYPE=FULL"
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
