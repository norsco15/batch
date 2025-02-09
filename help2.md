package com.example.extraction.batch;

import org.junit.jupiter.api.Test;

import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class DynamicRowMapperTest {

    @Test
    void testMapRow() throws SQLException {
        // GIVEN
        ResultSet rs = mock(ResultSet.class);
        ResultSetMetaData metaData = mock(ResultSetMetaData.class);

        when(rs.getMetaData()).thenReturn(metaData);
        when(metaData.getColumnCount()).thenReturn(2);

        // Simulons deux colonnes : "COL1" et "COL2"
        when(metaData.getColumnName(1)).thenReturn("COL1");
        when(metaData.getColumnName(2)).thenReturn("COL2");

        // Valeurs renvoyées par le ResultSet
        when(rs.getObject(1)).thenReturn("Value1");
        when(rs.getObject(2)).thenReturn(123);

        // WHEN
        DynamicRowMapper mapper = new DynamicRowMapper();
        Map<String, Object> result = mapper.mapRow(rs, 1);

        // THEN
        assertEquals(2, result.size());
        assertTrue(result.containsKey("COL1"));
        assertTrue(result.containsKey("COL2"));
        assertEquals("Value1", result.get("COL1"));
        assertEquals(123, result.get("COL2"));
    }
}
