<!-- Génération JAKARTA -->
<plugin>
  <groupId>org.glassfish.jaxb</groupId>
  <artifactId>maven-jaxb2-plugin</artifactId>
  <version>4.0.5</version>
  <executions>
    <execution>
      <goals><goal>generate</goal></goals>
      <configuration>
        <schemaDirectory>${project.basedir}/src/main/resources/xsd</schemaDirectory>
        <schemaIncludes><include>**/*.xsd</include></schemaIncludes>
        <generateDirectory>${project.build.directory}/generated-sources/jaxb</generateDirectory>
        <generatePackage>com.cacib.sfcm.interfaces.ssm.binding</generatePackage>
        <forceRegenerate>true</forceRegenerate>
      </configuration>
    </execution>
  </executions>
</plugin>

<!-- Runtime JAXB Jakarta -->
<dependency>
  <groupId>org.glassfish.jaxb</groupId>
  <artifactId>jaxb-runtime</artifactId>
  <version>4.0.5</version>
</dependency>



@Bean
public Jaxb2Marshaller dealEventMarshaller() {
  Jaxb2Marshaller m = new Jaxb2Marshaller();
  m.setContextPath("com.cacib.sfcm.interfaces.ssm.binding");
  return m;
}



// au lieu de createMarshaller(), fais :
StringWriter sw = new StringWriter();
marshaller.marshal(de, new StreamResult(sw));   // ← c’est le Jaxb2Marshaller Spring (Jakarta)
String xml = sw.toString();
