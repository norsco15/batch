@Data
@EqualsAndHashCode(callSuper = false)
public class JSonExtractionCSV {

    @JsonProperty
    private BigInteger extractionCSVId;

    @JsonProperty
    private String extpactionCSVSeparator;

    @JsonProperty
    private String extractionCSVHeader;

    @JsonProperty
    private String extractionDateFormat;

    @JsonProperty
    private String extractionNumberFormat;

    @JsonProperty
    private JSonExtractionSQL jsonExtractionSQL;

    /**
     * Nouveau : on veut stocker un objet JSON Format
     */
    @JsonProperty
    private JSonExtractionCSVFormat jsonExtractionCSVFormat;
}
