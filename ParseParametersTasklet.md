
# ─────────────────────────────────────────────────────────────────────────────
# pom.xml
# ─────────────────────────────────────────────────────────────────────────────
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.cacib.ssm</groupId>
  <artifactId>ssm-batch</artifactId>
  <version>1.0.0</version>
  <properties>
    <java.version>17</java.version>
    <spring-boot.version>3.3.3</spring-boot.version>
  </properties>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>${spring-boot.version}</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <dependencies>
    <!-- Spring Batch / JDBC / JMS -->
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-batch</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-data-jdbc</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-jms</artifactId>
    </dependency>

    <!-- JAXB (Java 17) -->
    <dependency>
      <groupId>org.glassfish.jaxb</groupId>
      <artifactId>jaxb-runtime</artifactId>
    </dependency>

    <!-- Oracle JDBC (licence à gérer en interne) -->
    <dependency>
      <groupId>com.oracle.database.jdbc</groupId>
      <artifactId>ojdbc8</artifactId>
      <version>23.2.0.0</version>
    </dependency>

    <!-- IBM MQ JMS client -->
    <dependency>
      <groupId>com.ibm.mq</groupId>
      <artifactId>com.ibm.mq.jakarta.client</artifactId>
      <version>9.4.3.0</version>
    </dependency>

    <!-- Lombok -->
    <dependency>
      <groupId>org.projectlombok</groupId>
      <artifactId>lombok</artifactId>
      <optional>true</optional>
    </dependency>

    <!-- Tests -->
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-test</artifactId>
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
        <version>0.14.0</version>
        <executions>
          <execution>
            <goals><goal>generate</goal></goals>
            <configuration>
              <schemaDirectory>${project.basedir}/src/main/resources/xsd</schemaDirectory>
              <schemas><schema>ssm.xsd</schema></schemas>
              <generateDirectory>${project.build.directory}/generated-sources/jaxb</generateDirectory>
              <generatePackage>com.cacib.ssm.binding</generatePackage>
              <args><arg>-no-header</arg></args>
            </configuration>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</project>


# ─────────────────────────────────────────────────────────────────────────────
# src/main/resources/application.properties
# ─────────────────────────────────────────────────────────────────────────────
spring.datasource.url=jdbc:oracle:thin:@//HOST:PORT/SERVICE
spring.datasource.username=${DB_USER}
spring.datasource.password=${DB_PASSWORD}
spring.datasource.driver-class-name=oracle.jdbc.OracleDriver

spring.jms.cache.enabled=true
spring.batch.job.enabled=false

ssm.mq.host=localhost
ssm.mq.port=1414
ssm.mq.channel=DEV.APP.SVRCONN
ssm.mq.queueManager=QM1
ssm.mq.queueName=SSM.OUT
ssm.mq.user=app
ssm.mq.password=secret

ssm.file.root-output=/tmp/out
ssm.file.filename-prefix=SSM_File
ssm.file.date-format=yyyyMMdd_HHmmss
ssm.file.extension=xml
ssm.file.prefix-with-event-id=true

ssm.xml.add-standalone-header=true

logging.level.root=INFO
logging.level.com.cacib.ssm=DEBUG


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/SSMBatchApplication.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm;

import lombok.RequiredArgsConstructor;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@RequiredArgsConstructor
public class SSMBatchApplication implements CommandLineRunner {
    private final JobLauncher jobLauncher;
    private final Job ssmJob;

    public static void main(String[] args) { SpringApplication.run(SSMBatchApplication.class, args); }

    @Override public void run(String... args) throws Exception {
        JobParameters params = new JobParametersBuilder()
                .addString("interface_code", arg(args, "interface_code", "4SIGHT"))
                .addString("company_code", arg(args, "company_code", "CLP"))
                .addString("outputpath", arg(args, "outputpath", "/tmp/out"))
                .addLong("ts", System.currentTimeMillis())
                .toJobParameters();
        jobLauncher.run(ssmJob, params);
    }
    private String arg(String[] args, String k, String d){ String p="--"+k+"="; for(String a:args) if(a.startsWith(p)) return a.substring(p.length()); return d; }
}


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/config/SSMBatchConfig.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.config;

import org.springframework.batch.core.configuration.annotation.DefaultBatchConfigurer;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SSMBatchConfig extends DefaultBatchConfigurer { }


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/config/SSMJmsConfig.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.config;

import com.ibm.mq.jakarta.jms.MQConnectionFactory;
import com.ibm.msg.client.jakarta.wmq.WMQConstants;
import jakarta.jms.ConnectionFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jms.core.JmsTemplate;

@Configuration
public class SSMJmsConfig {
    @Bean
    public ConnectionFactory mqConnectionFactory(
            @Value("${ssm.mq.host}") String host,
            @Value("${ssm.mq.port}") int port,
            @Value("${ssm.mq.channel}") String channel,
            @Value("${ssm.mq.queueManager}") String qm,
            @Value("${ssm.mq.user}") String user,
            @Value("${ssm.mq.password}") String password) throws Exception {
        MQConnectionFactory cf = new MQConnectionFactory();
        cf.setHostName(host); cf.setPort(port); cf.setChannel(channel); cf.setQueueManager(qm);
        cf.setTransportType(WMQConstants.WMQ_CM_CLIENT);
        cf.setStringProperty(WMQConstants.USERID, user);
        cf.setStringProperty(WMQConstants.PASSWORD, password);
        return cf;
    }
    @Bean public JmsTemplate jmsTemplate(ConnectionFactory cf){ return new JmsTemplate(cf); }
}


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/config/SSMJaxbConfig.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.oxm.jaxb.Jaxb2Marshaller;

@Configuration
public class SSMJaxbConfig {
    @Bean
    public Jaxb2Marshaller dealEventMarshaller() {
        Jaxb2Marshaller m = new Jaxb2Marshaller();
        m.setPackagesToScan("com.cacib.ssm.binding"); // généré depuis ssm.xsd
        return m;
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/config/batch/SSMJobConfig.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.config.batch;

import com.cacib.ssm.model.SSMModel;
import com.cacib.ssm.config.batch.reader.SSMItemReader;
import com.cacib.ssm.config.batch.processor.SSMItemProcessor;
import com.cacib.ssm.config.batch.writer.SSMWriterComposite;
import jakarta.xml.bind.JAXBElement;
import com.cacib.ssm.binding.DealEvent;
import lombok.RequiredArgsConstructor;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.item.ItemReader;
import org.springframework.batch.item.ItemWriter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;

@Configuration
@RequiredArgsConstructor
public class SSMJobConfig {

    @Bean
    public Job ssmJob(JobRepository jobRepository, Step ssmStep) {
        return new JobBuilder("ssmJob", jobRepository).start(ssmStep).build();
    }

    @Bean
    public Step ssmStep(JobRepository jobRepository, PlatformTransactionManager tx,
                        SSMItemReader reader,
                        SSMItemProcessor processor,
                        SSMWriterComposite writer) {
        return new StepBuilder("ssmStep", jobRepository)
                .<SSMModel, JAXBElement<DealEvent>>chunk(50, tx)
                .reader(reader)
                .processor(processor)
                .writer(writer)
                .faultTolerant().skip(Exception.class).skipLimit(Integer.MAX_VALUE)
                .build();
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/config/batch/reader/SSMItemReader.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.config.batch.reader;

import com.cacib.ssm.model.SSMModel;
import com.cacib.ssm.reader.SSMRowMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.item.ItemStreamException;
import org.springframework.batch.item.ItemStreamReader;
import org.springframework.batch.item.database.StoredProcedureItemReader;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Types;
import java.util.HashMap;
import java.util.Map;

@Component
@StepScope
@RequiredArgsConstructor
public class SSMItemReader implements ItemStreamReader<SSMModel> {
    private final DataSource dataSource;
    @Value("#{jobParameters['company_code']}") private String companyCode;
    private StoredProcedureItemReader<SSMModel> delegate;

    @Override public void open(org.springframework.batch.item.ExecutionContext ec) throws ItemStreamException {
        try {
            delegate = new StoredProcedureItemReader<>();
            delegate.setDataSource(dataSource);
            delegate.setProcedureName("usr_pkg_ssm.usr_ssm_on_the_fly");
            delegate.setParameters(new org.springframework.jdbc.core.SqlParameter[] {
                    new org.springframework.jdbc.core.SqlParameter("company_code", Types.VARCHAR),
                    new org.springframework.jdbc.core.SqlOutParameter("output", oracle.jdbc.OracleTypes.CURSOR)
            });
            Map<String,Object> pv = new HashMap<>(); pv.put("company_code", companyCode); delegate.setParameterValues(pv);
            delegate.setRowMapper(new SSMRowMapper());
            delegate.afterPropertiesSet();
            delegate.open(ec);
        } catch (Exception e) { throw new ItemStreamException(e); }
    }
    @Override public SSMModel read() throws Exception { return delegate.read(); }
    @Override public void update(org.springframework.batch.item.ExecutionContext ec) throws ItemStreamException { delegate.update(ec); }
    @Override public void close() throws ItemStreamException { delegate.close(); }
}


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/config/batch/processor/SSMItemProcessor.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.config.batch.processor;

import com.cacib.ssm.binding.*;
import com.cacib.ssm.model.SSMModel;
import jakarta.xml.bind.JAXBElement;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.*;

@Component
@StepScope
public class SSMItemProcessor implements ItemProcessor<SSMModel, JAXBElement<DealEvent>> {
    @Value("#{jobParameters['interface_code']}") private String interfaceCode;

    @Override
    public JAXBElement<DealEvent> process(SSMModel model) throws Exception {
        ObjectFactory of = new ObjectFactory();
        DealEvent de = of.createDealEvent();
        String app = (interfaceCode == null || interfaceCode.isBlank()) ? "4SIGHT" : interfaceCode;
        de.setApplicationCode(app);
        de.setEventType(model.getMvtType());

        var df = jakarta.xml.datatype.DatatypeFactory.newInstance();
        Calendar in = Calendar.getInstance(); if (model.getInputDateTimestamp()!=null) in.setTime(model.getInputDateTimestamp());
        var execDate = df.newXMLGregorianCalendar(in.get(Calendar.YEAR), in.get(Calendar.MONTH)+1,
                in.get(Calendar.DAY_OF_MONTH), in.get(Calendar.HOUR_OF_DAY), in.get(Calendar.MINUTE),
                in.get(Calendar.SECOND), in.get(Calendar.MILLISECOND), (in.get(Calendar.ZONE_OFFSET)+in.get(Calendar.DST_OFFSET))/60000);
        Calendar tr = Calendar.getInstance(); if (model.getTradeDate()!=null) tr.setTime(model.getTradeDate());
        var tradeDate = df.newXMLGregorianCalendar(tr.get(Calendar.YEAR), tr.get(Calendar.MONTH)+1,
                tr.get(Calendar.DAY_OF_MONTH), tr.get(Calendar.HOUR_OF_DAY), tr.get(Calendar.MINUTE),
                tr.get(Calendar.SECOND), tr.get(Calendar.MILLISECOND), (tr.get(Calendar.ZONE_OFFSET)+tr.get(Calendar.DST_OFFSET))/60000);

        de.setEventDateTime(execDate); de.setEventSequenceId(model.getEventId());

        DealEvent.Execution exec = of.createDealEventExecution();
        exec.setExecutionDateTime(execDate);
        if (model.getPrice()!=null) exec.setPrice(model.getPrice());
        if (model.getQuantity()!=null) { exec.setQuantity(model.getQuantity()); exec.setDiffQuantity(model.getQuantity()); }
        exec.setValueDate(tradeDate); exec.setPaymentCurrencyId(model.getCurrency()); exec.setSide(model.getDirection()); exec.setFolioId(0L);

        DealEvent.Execution.ExecutionRefs execRefs = of.createDealEventExecutionExecutionRefs();
        DealEvent.Execution.ExecutionRefs.Ref execRef = of.createDealEventExecutionExecutionRefsRef();
        execRef.setReferentialName(app);
        execRef.setReference(model.getTransactionId()!=null? String.valueOf(model.getTransactionId()) : "0");
        execRefs.getRef().add(execRef); exec.setExecutionRefs(execRefs);

        DealEvent.Execution.Product product = of.createDealEventExecutionProduct();
        DealEvent.Execution.Product.ProductRefs productRefs = of.createDealEventExecutionProductProductRefs();
        DealEvent.Execution.Product.ProductRefs.Ref productRef = of.createDealEventExecutionProductProductRefsRef();
        productRef.setReferentialName(app);
        productRef.setReference((model.getStockCode()!=null?model.getStockCode():"") + (model.getMarketCode()!=null?"|"+model.getMarketCode():""));
        productRefs.getRef().add(productRef); product.setProductRefs(productRefs);
        product.setLegalWrapperType(model.getType()); product.setCurrencyId(model.getStockCurrency()); product.setName(model.getStockName());
        exec.setProduct(product);

        DealEvent.Execution.Broker broker = of.createDealEventExecutionBroker(); broker.setName("DEAL INTERNE"); broker.setReference("INTERNAL"); broker.setFees(BigDecimal.ZERO); exec.setBroker(broker);
        DealEvent.Execution.Operator op = of.createDealEventExecutionOperator(); op.setOperatorId(model.getUserCode()); op.setName(model.getUserName()); exec.setOperator(op);
        DealEvent.Execution.Order order = of.createDealEventExecutionOrder(); DealEvent.Execution.Order.MarketPlace mp = of.createDealEventExecutionOrderMarketPlace(); mp.setFees(BigDecimal.ZERO); mp.setName(model.getMarketCode()); order.setMarketPlace(mp); exec.setOrder(order);

        DealEvent.Execution.LifeCycle lc = of.createDealEventExecutionLifeCycle();
        List<DealEvent.Execution.LifeCycle.Step> steps = lc.getStep(); var now = df.newXMLGregorianCalendar(new GregorianCalendar());
        DealEvent.Execution.LifeCycle.Step s1 = of.createDealEventExecutionLifeCycleStep(); s1.setDateTime(now); s1.setComponent(app); s1.setIndex((short)0);
        DealEvent.Execution.LifeCycle.Step s2 = of.createDealEventExecutionLifeCycleStep(); s2.setDateTime(now); s2.setComponent(app); s2.setIndex((short)1); s2.setFrom("EMS_DISPATCHER"); s2.setTo("DISPATCHER_SSM_EU_XETRA");
        steps.add(s1); steps.add(s2); exec.setLifeCycle(lc);

        DealEvent.Execution.SsmInfo si = of.createDealEventExecutionSsmInfo(); DealEvent.Execution.SsmInfo.SsmZoneActivity za = of.createDealEventExecutionSsmInfoSsmZoneActivity(); za.setActivity("Others"); za.setCcy(model.getCurrency()); za.setZone("Europe"); si.setSsmZoneActivity(za); exec.setSsmInfo(si);

        de.setExecution(exec);
        return of.createDealEvent(de);
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/config/batch/writer/SSMWriterComposite.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.config.batch.writer;

import com.cacib.ssm.binding.DealEvent;
import com.cacib.ssm.service.SSMStatusService;
import jakarta.xml.bind.JAXBElement;
import lombok.extern.slf4j.Slf4j;
import org.springframework.batch.core.ExitStatus;
import org.springframework.batch.core.StepExecution;
import org.springframework.batch.core.StepExecutionListener;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.item.ItemWriter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jms.core.JmsTemplate;
import org.springframework.oxm.jaxb.Jaxb2Marshaller;
import org.springframework.stereotype.Component;

import javax.xml.transform.stream.StreamResult;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.text.SimpleDateFormat;
import java.util.*;

@Slf4j
@Component
@StepScope
public class SSMWriterComposite implements ItemWriter<JAXBElement<DealEvent>>, StepExecutionListener {

    private final JmsTemplate jmsTemplate;
    private final SSMStatusService statusService;
    private final Jaxb2Marshaller marshaller;

    public SSMWriterComposite(JmsTemplate jmsTemplate, SSMStatusService statusService, Jaxb2Marshaller marshaller) {
        this.jmsTemplate = jmsTemplate; this.statusService = statusService; this.marshaller = marshaller;
    }

    @Value("#{jobParameters['company_code']}") private String companyCode;
    @Value("#{jobParameters['outputpath']}") private String outputPath;
    @Value("${ssm.mq.queueName}") private String queueName;

    @Value("${ssm.file.filename-prefix:SSM_File}") private String filenamePrefix;
    @Value("${ssm.file.date-format:yyyyMMdd_HHmmss}") private String dateFormat;
    @Value("${ssm.file.extension:xml}") private String extension;
    @Value("${ssm.file.prefix-with-event-id:true}") private boolean prefixWithEventId;
    @Value("${ssm.xml.add-standalone-header:true}") private boolean addStandaloneHeader;

    private final Map<String,String> results = new LinkedHashMap<>();

    @Override public void beforeStep(StepExecution stepExecution) { results.clear(); }

    @Override
    public void write(List<? extends JAXBElement<DealEvent>> items) throws Exception {
        SimpleDateFormat sdf = new SimpleDateFormat(dateFormat);
        String ts = sdf.format(new Date());
        Path base = Path.of(outputPath, companyCode, "SSM"); Files.createDirectories(base);

        for (JAXBElement<DealEvent> el : items) {
            DealEvent de = el.getValue(); String eventId = String.valueOf(de.getEventSequenceId());
            try {
                // Marshal → XML
                StringWriter sw = new StringWriter();
                var m = marshaller.createMarshaller();
                m.setProperty(jakarta.xml.bind.Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);
                m.marshal(el, new StreamResult(sw)); String xml = sw.toString();
                if (addStandaloneHeader) {
                    if (!xml.startsWith("<?xml")) xml = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
" + xml;
                    else if (!xml.contains("standalone=\"yes\"")) xml = xml.replaceFirst("<\?xml([^>]*)\?>","<?xml$1 standalone=\"yes\"?>");
                }
                // Fichier
                String baseName = filenamePrefix + ts + "." + extension;
                String filename = prefixWithEventId ? (eventId + "_" + baseName) : baseName;
                Files.writeString(base.resolve(filename), xml, StandardCharsets.UTF_8);
                // MQ
                jmsTemplate.convertAndSend(queueName, xml);
                results.put(eventId, "Y");
            } catch (Exception ex) { log.error("Erreur sortie pour event {}", eventId, ex); results.put(eventId, "R"); }
        }
    }

    @Override public ExitStatus afterStep(StepExecution stepExecution) {
        try { statusService.updateStatuses(results); } catch (Exception e) { log.error("Erreur MAJ statuts", e); }
        try { statusService.archive(); } catch (Exception e) { log.error("Erreur archivage", e); }
        return ExitStatus.COMPLETED;
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/repository/SSMRepository.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.repository;

import org.springframework.data.jdbc.repository.query.Modifying;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.Repository;
import org.springframework.data.repository.query.Param;

import com.cacib.ssm.model.SSMExtEvent; // aggregate marker for Spring Data JDBC

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


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/model/SSMExtEvent.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Table;
import lombok.Data;

@Data
@Table("EXT_EVENT")
public class SSMExtEvent {
    @Id
    private Long eventId;
    private String extProcessed; // facultatif; utilisé comme agrégat minimal
}


# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.repository.impl;

import com.cacib.ssm.repository.SSMRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class SSMRepositoryImpl implements SSMRepository {
    private final JdbcTemplate jdbc;

    @Override
    public void markExtProcessed(Long eventId, String flag) {
        jdbc.update("update EXT_EVENT set EXT_PROCESSED = ? where EVENT_ID = ?", flag, eventId);
    }

    @Override
    public void markSsmProcessed(Long eventId, String flag) {
        jdbc.update("update USR_POS_LOADER set SSM_EXT_PROCESSED = ? where EVT_NUM_SEQID = ?", flag, eventId);
    }

    @Override
    public void archive() {
        jdbc.update("begin usr_pkg_ssm.usr_ssm_archive(); end;");
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/service/SSMStatusService.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.service;

import com.cacib.ssm.repository.SSMRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service @RequiredArgsConstructor @Slf4j
public class SSMStatusService {
    private final SSMRepository repo;
    public void updateStatuses(Map<String,String> results) {
        results.forEach((eventId, flag) -> {
            Long id = Long.valueOf(eventId);
            repo.markExtProcessed(id, flag);
            repo.markSsmProcessed(id, flag);
            log.info("Updated statuses for {} -> {}", eventId, flag);
        });
    }
    public void archive() { repo.archive(); }
}


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/model/SSMModel.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.model;

import lombok.Data;
import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

@Data
public class SSMModel implements Serializable {
    private String eventCode;
    private String mvtType;
    private Long eventId;
    private Long transactionId;
    private Date inputDateTimestamp;
    private BigDecimal price;
    private BigDecimal quantity;
    private Date tradeDate;
    private String currency;
    private String stockCode;
    private String stockName;
    private String marketCode;
    private String stockCurrency;
    private String userCode;
    private String userName;
    private String type;
    private String direction;
    private Long necId;
    private Long tradeRef;
    private Long settlementId;
    private String corporateActionType;
}


# ─────────────────────────────────────────────────────────────────────────────
# src/main/java/com/cacib/ssm/reader/SSMRowMapper.java
# ─────────────────────────────────────────────────────────────────────────────
package com.cacib.ssm.reader;

import com.cacib.ssm.model.SSMModel;
import org.springframework.jdbc.core.RowMapper;
import java.sql.ResultSet; import java.sql.SQLException;

public class SSMRowMapper implements RowMapper<SSMModel> {
    @Override public SSMModel mapRow(ResultSet rs, int rowNum) throws SQLException {
        SSMModel m = new SSMModel();
        m.setEventCode(rs.getString("EVT_TXT_EVT_CODE"));
        m.setMvtType(rs.getString("EVT_TXT_MVT_TYPE"));
        m.setEventId(rs.getLong("EVI_NUM_SEQID"));
        m.setTransactionId(rs.getLong("TRS_NUM_ID"));
        m.setInputDateTimestamp(rs.getTimestamp("EVT_TSP_EXEC_DATE"));
        m.setPrice(rs.getBigDecimal("TRS_NUM_PRC"));
        m.setQuantity(rs.getBigDecimal("TRS_NUM_QTY"));
        m.setTradeDate(rs.getTimestamp("TRS_DTE_VALUE"));
        m.setCurrency(rs.getString("PMT_TXT_CCY_ID"));
        m.setStockCode(rs.getString("REF_TXT_STK_ID"));
        m.setStockName(rs.getString("STK_TXT_NME"));
        m.setMarketCode(rs.getString("STK_TXT_MKT_PLACE"));
        m.setStockCurrency(rs.getString("STK_TXT_CCY_CDE"));
        m.setUserCode(rs.getString("EVT_TXT_USR_ID"));
        m.setUserName(rs.getString("USR_TXT_NAME"));
        m.setType(rs.getString("TRS_TXT_MVT_ORIGIN"));
        m.setDirection(rs.getString("TRS_TXT_SIDE"));
        m.setNecId(rs.getLong("NCE_NUM_NC_COLLAT_ID"));
        m.setTradeRef(rs.getLong("TRS_NUM_MVT_ID"));
        m.setSettlementId(rs.getLong("TRS_NUM_SETT_ID"));
        return m;
    }
}
