package com.mycompany.extraction.batch.util;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import org.springframework.batch.core.JobParameters;

public class JobParametersUtilTest {

    @Test
    void testCreateJobParameters() {
        String[] args = {
            "--extractionId=123", 
            "--paramList=ENV=PREPROD;TYPE=FULL"
        };

        JobParameters jobParams = JobParametersUtil.createJobParameters(args);
        assertEquals("123", jobParams.getString("extractionId"));
        assertEquals("ENV=PREPROD;TYPE=FULL", jobParams.getString("paramList"));
        assertNotNull(jobParams.getString("time"));
        // "time" est un param auto
    }

    @Test
    void testNoArgs() {
        String[] args = {};
        JobParameters jobParams = JobParametersUtil.createJobParameters(args);
        // On a juste "time"
        assertNotNull(jobParams.getString("time"));
        assertNull(jobParams.getString("extractionId"));
    }
}
