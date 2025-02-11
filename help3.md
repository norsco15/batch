package com.example.extraction.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.math.BigInteger;

@Data
public class JSonExtractionCSVFormat {
    
    @JsonProperty
    private BigInteger extractionCSVFormatId;

    /**
     * Par exemple "EVENT_ID;LOAN_ID" pour exclure ces headers du formattage numérique.
     */
    @JsonProperty
    private String excludedHeaders;
}
