@Override
public void open(ExecutionContext ec) throws ItemStreamException {
  try {
    delegate = new StoredProcedureItemReader<>();
    delegate.setDataSource(dataSource);
    delegate.setProcedureName("usr_pkg_ssm.usr_ssm_on_the_fly");
    delegate.setParameters(new org.springframework.jdbc.core.SqlParameter[]{
        new org.springframework.jdbc.core.SqlParameter("p_company_code", java.sql.Types.VARCHAR),
        new org.springframework.jdbc.core.SqlOutParameter("p_out", oracle.jdbc.OracleTypes.CURSOR)
    });
    // IMPORTANT : setter qui renseigne l'IN + enregistre l'OUT (index 2)
    delegate.setPreparedStatementSetter(ps -> {
      java.sql.CallableStatement cs = (java.sql.CallableStatement) ps;
      cs.setString(1, companyCode);
      cs.registerOutParameter(2, oracle.jdbc.OracleTypes.CURSOR);
    });
    // (optionnel selon la version) :
    // delegate.setRefCursorPosition(2);

    delegate.setRowMapper(new SSMRowMapper());
    delegate.afterPropertiesSet();
    delegate.open(ec);
  } catch (Exception e) {
    throw new ItemStreamException(e);
  }
}
