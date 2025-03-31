package com.example.monthlypnl.tasklet;

import com.example.monthlypnl.constants.MonthlyPnLConstant;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.simple.SimpleJdbcCall;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.batch.repeat.RepeatStatus;

import javax.sql.DataSource;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Component
public class MonthlyPnLTasklet implements Tasklet {

    private static final Logger LOG = LogManager.getLogger(MonthlyPnLTasklet.class);

    // Pour faire des requêtes simples
    private final JdbcTemplate jdbcTemplate;

    // Pour appeler la procédure

    @Override
    @Transactional
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
        LOG.info("=== ENTER: MonthlyPnLTasklet.execute() ===");

        try {
            // 1) Ré    private final SimpleJdbcCall callProcedure;

    @Autowired
    public MonthlyPnLTasklet(DataSource dataSource) {
        this.jdbcTemplate = new JdbcTemplate(dataSource);

        // On prépare l'appel de la procédure stockée :
        this.callProcedure = new SimpleJdbcCall(this.jdbcTemplate)
                .withProcedureName("CLY_Rpt_pl_ext_viewer_get");
        // Optionnellement, tu peux déclarer les paramètres IN si la DB en a besoin.
    }
cupérer le profit centre en base si besoin
            String profitCentreId = null;
            try {
                profitCentreId = jdbcTemplate.queryForObject(
                    "SELECT profit_centre_id FROM al_profit_centre WHERE profit_centre_mnemonic = 'CLP'",
                    String.class
                );
            } catch (Exception e) {
                LOG.error("Unable to retrieve profit centre ID from DB", e);
            }

            // 2) Construire la map de paramètres
            Map<String, Object> inParams = new HashMap<>();
            inParams.put("p_user_id", MonthlyPnLConstant.USER_ID);
            inParams.put("p_groupby_filter", MonthlyPnLConstant.GROUP_BY_FILTER);
            inParams.put("p_profit_centre_id", profitCentreId);
            inParams.put("p_realised_flag", MonthlyPnLConstant.REALISED_FLAG);
            inParams.put("p_use_client_code", MonthlyPnLConstant.USE_CLIENT_CODE);
            inParams.put("p_client_code", MonthlyPnLConstant.CLIENT_CODE);
            inParams.put("p_use_stock_mnemonic", MonthlyPnLConstant.USE_STOCK_MNEMONIC);
            inParams.put("p_stock_mnemonic", MonthlyPnLConstant.STOCK_MNEMONIC);
            inParams.put("p_use_company_bank_code", MonthlyPnLConstant.USE_COMPANY_BANK_CODE);
            inParams.put("p_company_bank_code", MonthlyPnLConstant.COMPANY_BANK_CODE);
            inParams.put("p_use_company_bank_account", MonthlyPnLConstant.USE_COMPANY_BANK_ACCOUNT);
            inParams.put("p_company_bank_account", MonthlyPnLConstant.COMPANY_BANK_ACCOUNT);
            inParams.put("p_use_trade_ref", MonthlyPnLConstant.USE_TRADE_REF);
            inParams.put("p_trade_ref", MonthlyPnLConstant.TRADE_REF);
            inParams.put("p_use_trade_ref_type", MonthlyPnLConstant.USE_TRADE_REF_TYPE);
            inParams.put("p_trade_ref_type", MonthlyPnLConstant.TRADE_REF_TYPE);
            inParams.put("p_use_market_code", MonthlyPnLConstant.USE_MARKET_CODE);
            inParams.put("p_market_code", MonthlyPnLConstant.MARKET_CODE);
            inParams.put("p_use_currency_code", MonthlyPnLConstant.USE_CURRENCY_CODE);
            inParams.put("p_currency_code", MonthlyPnLConstant.CURRENCY_CODE);
            inParams.put("p_report_currency_code", MonthlyPnLConstant.REPORT_CURRENCY_CODE);
            inParams.put("p_effective_date", new Date()); // ex: date du jour
            inParams.put("p_client_type_code", MonthlyPnLConstant.CLIENT_TYPE_CODE);
            inParams.put("p_security_country_code", MonthlyPnLConstant.SECURITY_CODE);
            inParams.put("p_separate_div_currencies", MonthlyPnLConstant.SEPARATE_DIV_CURRENCIES);

            LOG.info("Calling stored procedure with parameters: {}", inParams);

            // 3) Appeler la procédure stockée
            callProcedure.execute(inParams);

            LOG.info("=== Procedure call successful ===");
        } catch (Exception e) {
            LOG.error("Error while executing MonthlyPnL procedure", e);
            throw new RuntimeException("MonthlyPnLTasklet failed", e);
        }

        LOG.info("=== EXIT: MonthlyPnLTasklet.execute() ===");
        return RepeatStatus.FINISHED;
    }
}
