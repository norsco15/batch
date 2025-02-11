@Data
@Entity
@Table(name = "USR_EXTRACTION_CSV")
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
public class SFCMExtractionCSVEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "UsrExtractionCSVSequence")
    @SequenceGenerator(name = "UsrExtractionCSVSequence", sequenceName = "USR_EXTRACTION_CSV_SEQUENCE", allocationSize = 1)
    @Column(name = "extraction_csv_id")
    @EqualsAndHashCode.Include
    private BigInteger extractionCSVId;

    @Column(name = "extraction_csv_separator")
    private String extractionCSVSeparator;

    @Column(name = "extraction_csv_header")
    @Lob
    private String extractionCSVHeader;

    @Column(name = "extraction_date_format")
    private String extractionDateFormat;

    @Column(name = "extraction_number_format")
    private String extractionNumberFormat;

    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "extraction_id")
    private SFCMExtractionEntity extractionEntity;

    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "extraction_sql_id")
    private SFCMExtractionSQLEntity extractionSQLEntity;

    /**
     * Nouvelle relation OneToOne vers l'entité CSVFormat.
     * Ici, le mappedBy n'est pas nécessaire si on garde la clé
     * dans SFCMExtractionCSVFormatEntity. 
     */
    @OneToOne(mappedBy = "extractionCSVEntity", cascade = CascadeType.ALL)
    private SFCMExtractionCSVFormatEntity extractionCSVFormatEntity;
}
