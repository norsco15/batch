package com.mycompany.extraction.batch.util;

import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import java.util.Properties;

public class JobParametersUtil {

    private JobParametersUtil() {
        // classe util statique
    }

    public static JobParameters createJobParameters(String[] args) {
        Properties props = new Properties();
        for(String arg : args){
            if(arg.startsWith("--")){
                String[] kv = arg.substring(2).split("=",2);
                if(kv.length==2){
                    props.put(kv[0], kv[1]);
                }
            }
        }
        props.put("time", String.valueOf(System.currentTimeMillis()));

        JobParametersBuilder builder = new JobParametersBuilder();
        for(String name : props.stringPropertyNames()){
            builder.addString(name, props.getProperty(name));
        }
        return builder.toJobParameters();
    }
}
