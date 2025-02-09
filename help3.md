package com.example.extraction.controller;

import com.example.extraction.model.JSonExtraction;
import com.example.extraction.model.JSonLaunchExtraction;
import com.example.extraction.service.SFCMExtractionService;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigInteger;
import java.util.Collections;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(SCMExtractionController.class)
class SCMExtractionControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private SFCMExtractionService service;

    @Test
    void testSave() throws Exception {
        JSonExtraction mockExtraction = new JSonExtraction();
        mockExtraction.setExtractionId(BigInteger.ONE);
        mockExtraction.setExtractionName("TestName");

        when(service.save(any(JSonExtraction.class))).thenReturn(mockExtraction);

        mockMvc.perform(post("/api/extraction/save")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"extractionName\":\"TestName\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.extractionId").value(1))
                .andExpect(jsonPath("$.extractionName").value("TestName"));
    }

    @Test
    void testLoadAll() throws Exception {
        JSonExtraction mockExtraction = new JSonExtraction();
        mockExtraction.setExtractionId(BigInteger.ONE);
        mockExtraction.setExtractionName("TestName");

        when(service.loadALL()).thenReturn(Collections.singletonList(mockExtraction));

        mockMvc.perform(get("/api/extraction/load_all"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].extractionId").value(1))
                .andExpect(jsonPath("$[0].extractionName").value("TestName"));
    }

    @Test
    void testLoadOne() throws Exception {
        JSonExtraction mockExtraction = new JSonExtraction();
        mockExtraction.setExtractionId(BigInteger.ONE);
        mockExtraction.setExtractionName("TestName");

        when(service.load_one(BigInteger.ONE)).thenReturn(mockExtraction);

        mockMvc.perform(get("/api/extraction/load_one/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.extractionId").value(1))
                .andExpect(jsonPath("$.extractionName").value("TestName"));
    }

    @Test
    void testUpdate() throws Exception {
        JSonExtraction mockExtraction = new JSonExtraction();
        mockExtraction.setExtractionId(BigInteger.ONE);
        mockExtraction.setExtractionName("UpdatedName");

        when(service.update(any(JSonExtraction.class))).thenReturn(mockExtraction);

        mockMvc.perform(put("/api/extraction/update")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"extractionId\":1,\"extractionName\":\"UpdatedName\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.extractionId").value(1))
                .andExpect(jsonPath("$.extractionName").value("UpdatedName"));
    }

    @Test
    void testLaunch() throws Exception {
        doNothing().when(service).launch(any(JSonLaunchExtraction.class));

        mockMvc.perform(post("/api/extraction/launch")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"extractionId\":123}"))
                .andExpect(status().isOk())
                .andExpect(content().string("Batch Job launched successfully!"));

        verify(service, times(1)).launch(any(JSonLaunchExtraction.class));
    }

    @Test
    void testDelete() throws Exception {
        doNothing().when(service).delete(BigInteger.ONE);

        mockMvc.perform(delete("/api/extraction/delete/1"))
                .andExpect(status().isOk())
                .andExpect(content().string("Delete successfully!"));

        verify(service, times(1)).delete(BigInteger.ONE);
    }

}
