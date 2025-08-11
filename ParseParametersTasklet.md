<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.1.5</version> <!-- ok de garder 3.1.x si ton projet est aligné -->
    <relativePath/>
  </parent>

  <groupId>com.cacib.sfcm.interfaces</groupId>
  <artifactId>sfcm-ssm</artifactId>
  <version>1.0.0-SNAPSHOT</version>

  <properties>
    <java.version>17</java.version>
  </properties>

  <dependencies>
    <!-- Spring -->
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-batch</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-data-jdbc</artifactId> <!-- pour Repository interface @Query (Data JDBC) -->
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-jms</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-oxm</artifactId> <!-- Jaxb2Marshaller -->
    </dependency>

    <!-- Oracle JDBC -->
    <dependency>
      <groupId>com.oracle.database.jdbc</groupId>
      <artifactId>ojdbc8</artifactId>
      <version>23.2.0.0</version>
    </dependency>

    <!-- IBM MQ Jakarta (Spring Boot 3) -->
    <dependency>
      <groupId>com.ibm.mq</groupId>
      <artifactId>com.ibm.mq.jakarta.client</artifactId>
      <version>9.4.3.0</version>
    </dependency>

    <!-- JAXB pour Java 17 -->
    <dependency>
      <groupId>org.glassfish.jaxb</groupId>
      <artifactId>jaxb-runtime</artifactId>
    </dependency>

    <!-- Tests -->
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-test</artifactId>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.springframework.batch</groupId>
      <artifactId>spring-batch-test</artifactId>
      <scope>test</scope>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
      </plugin>

      <!-- Génération JAXB depuis ssm.xsd -->
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
              <!-- Choisis 1 des deux variantes ci-dessous -->

              <!-- Variante A (simple) : inclure des fichiers précis -->
              <schemaIncludes>
                <include>ssm.xsd</include>
              </schemaIncludes>

              <!-- Variante B (avec fileset)
              <schemas>
                <schema>
                  <fileset>
                    <directory>${project.basedir}/src/main/resources/xsd</directory>
                    <includes>
                      <include>ssm.xsd</include>
                    </includes>
                  </fileset>
                </schema>
              </schemas>
              -->

              <generateDirectory>${project.build.directory}/generated-sources/jaxb</generateDirectory>
              <!-- Mets le package qui te convient : -->
              <generatePackage>com.cacib.sfcm.interfaces.ssm.binding</generatePackage>
              <args>
                <arg>-no-header</arg>
              </args>
            </configuration>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</project>



MQConnectionFactory cf = new MQConnectionFactory();
cf.setHostName(host);
cf.setPort(port);
cf.setChannel(channel);
cf.setQueueManager(qm);
cf.setTransportType(WMQConstants.WMQ_CM_CLIENT);
cf.setBooleanProperty(WMQConstants.USER_AUTHENTICATION_MQCSP, true);
cf.setStringProperty(WMQConstants.USERID, user);
cf.setStringProperty(WMQConstants.PASSWORD, password);



m.setProperty(jakarta.xml.bind.Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);





import org.springframework.data.jdbc.repository.query.Modifying;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.Repository;
import org.springframework.data.repository.query.Param;

public interface SSMRepository extends Repository<SSMExtEvent, Long> {
  @Modifying
  @Query("UPDATE EXT_EVENT SET EXT_PROCESSED = :flag WHERE EVENT_ID = :eventId")
  void markExtProcessed(@Param("eventId") Long eventId, @Param("flag") String flag);

  @Modifying
  @Query("UPDATE USR_POS_LOADER SET SSM_EXT_PROCESSED = :flag WHERE EVT_NUM_SEQID = :eventId")
  void markSsmProcessed(@Param("eventId") Long eventId, @Param("flag") String flag);

  @Modifying
  @Query("CALL usr_pkg_ssm.usr_ssm_archive()")
  void archive();
}
