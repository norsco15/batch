<plugin>
  <groupId>org.jvnet.jaxb2.maven2</groupId>
  <artifactId>maven-jaxb2-plugin</artifactId>
  <version>0.15.3</version>
  <executions>
    <execution>
      <goals>
        <goal>generate</goal>
      </goals>
      <configuration>
        <!-- Dossier où se trouve ssm.xsd -->
        <schemaDirectory>${project.basedir}/src/main/resources/xsd</schemaDirectory>

        <!-- Inclus avec wildcard pour ne pas se planter sur le nom -->
        <schemaIncludes>
          <include>**/*.xsd</include>
        </schemaIncludes>

        <!-- Où générer le code -->
        <generateDirectory>${project.build.directory}/generated-sources/jaxb</generateDirectory>

        <!-- Le package Java des classes générées -->
        <generatePackage>com.cacib.sfcm.interfaces.ssm.binding</generatePackage>

        <forceRegenerate>true</forceRegenerate>
        <args>
          <arg>-no-header</arg>
        </args>
      </configuration>
    </execution>
  </executions>
</plugin>
