const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  // Patient endpoints
  async createPatient(patientData) {
    const response = await fetch(`${API_BASE_URL}/patients/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientData),
    });
    if (!response.ok) throw new Error('Failed to create patient');
    return response.json();
  },

  async getPatient(patientId) {
    const response = await fetch(`${API_BASE_URL}/patients/${patientId}`);
    if (!response.ok) throw new Error('Failed to fetch patient');
    return response.json();
  },

  async getPatientHistory(patientId) {
    const response = await fetch(`${API_BASE_URL}/patients/${patientId}/history`);
    if (!response.ok) throw new Error('Failed to fetch patient history');
    return response.json();
  },

  // Lab Report endpoints
  async uploadLabReport(patientId, reportDate, file) {
    const formData = new FormData();
    formData.append('patient_id', patientId);
    formData.append('report_date', reportDate);
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/reports/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error('Failed to upload lab report');
    return response.json();
  },

  async getReport(reportId) {
    const response = await fetch(`${API_BASE_URL}/reports/${reportId}`);
    if (!response.ok) throw new Error('Failed to fetch report');
    return response.json();
  },

  // Diet Plan endpoints
  async generateDietPlan(reportId) {
    const response = await fetch(`${API_BASE_URL}/diet/generate/${reportId}`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to generate diet plan');
    return response.json();
  },

  async getDietPlan(planId) {
    const response = await fetch(`${API_BASE_URL}/diet/${planId}`);
    if (!response.ok) throw new Error('Failed to fetch diet plan');
    return response.json();
  },

  // Health check
  async healthCheck() {
    const response = await fetch('http://localhost:8000/health');
    return response.json();
  },
};
