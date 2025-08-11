<!-- Génération du modèle Jakarta (DealEvent, ObjectFactory, …) depuis ssm.xsd -->
<plugin>
  <groupId>org.glassfish.jaxb</groupId>
  <artifactId>jaxb-maven-plugin</artifactId>
  <version>4.0.5</version>
  <executions>
    <execution>
      <goals>
        <goal>xjc</goal>
      </goals>
      <configuration>
        <!-- ton XSD -->
        <sources>
          <source>${project.basedir}/src/main/resources/xsd/ssm.xsd</source>
        </sources>

        <!-- package Java généré -->
        <packageName>com.cacib.sfcm.interfaces.ssm.binding</packageName>

        <!-- dossier de génération -->
        <outputDirectory>${project.build.directory}/generated-sources/jaxb</outputDirectory>

        <!-- optionnel -->
        <arguments>
          <argument>-no-header</argument>
        </arguments>

        <!-- ajoute auto le dossier généré au classpath -->
        <addCompileSourceRoot>true</addCompileSourceRoot>
      </configuration>
    </execution>
  </executions>
</plugin>
