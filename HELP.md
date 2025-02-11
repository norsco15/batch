package com.example.extraction.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

import javax.persistence.*;
import java.math.BigInteger;

@Data
@Entity
@Table(name = "USR_EXTRACTION_CSV_FORMAT")
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
public class SFCMExtractionCSVFormatEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "UsrExtractionCSVFormatSequence")
    @SequenceGenerator(name = "UsrExtractionCSVFormatSequence", sequenceName = "USR_EXTRACTION_CSV_FORMAT_SEQ", allocationSize = 1)
    @Column(name = "extraction_csv_format_id")
    @EqualsAndHashCode.Include
    private BigInteger extractionCSVFormatId;

    /**
     * On stocke ici la liste des headers à exclure du formattage numérique, 
     * par exemple "EVENT_ID;LOAN_ID".
     */
    @Column(name = "excluded_headers")
    private String excludedHeaders;

    /**
     * Relation OneToOne avec SFCMExtractionCSVEntity.
     * Ce côté-ci détient la clé étrangère (extraction_csv_id).
     */
    @OneToOne
    @JoinColumn(name = "extraction_csv_id") 
    private SFCMExtractionCSVEntity extractionCSVEntity;
}
