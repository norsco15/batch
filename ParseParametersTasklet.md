<plugin>
  <groupId>org.glassfish.jaxb</groupId>
  <artifactId>maven-jaxb2-plugin</artifactId>
  <version>4.0.5</version>
  <executions>
    <execution>
      <goals><goal>generate</goal></goals>
      <configuration>
        <schemaDirectory>${project.basedir}/src/main/resources/xsd</schemaDirectory>
        <schemaIncludes>
          <include>**/*.xsd</include>
        </schemaIncludes>
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
<!-- (optionnel, en général inclus par jaxb-runtime) -->
<dependency>
  <groupId>jakarta.xml.bind</groupId>
  <artifactId>jakarta.xml.bind-api</artifactId>
  <version>4.0.2</version>
</dependency>
