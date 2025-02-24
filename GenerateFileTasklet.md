package com.mycompany.extraction.batch;

import org.springframework.batch.core.*;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.stereotype.Component;

import java.nio.file.Files;
import java.nio.file.Paths;

@Component
public class GenerateFileTasklet implements Tasklet {
    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
        // Ex: on récupère un “fichier” depuis un param
        // Ex: on écrit un CSV localement
        String content = "Exemple de contenu\n...";
        Files.write(Paths.get("output.csv"), content.getBytes());
        System.out.println("File output.csv generated!");
        return RepeatStatus.FINISHED;
    }
}
