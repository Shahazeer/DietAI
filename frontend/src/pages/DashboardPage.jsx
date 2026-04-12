import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import ReportHistoryTable from '../components/ReportHistoryTable';
import ReportDetailPanel from '../components/ReportDetailPanel';

export default function DashboardPage() {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loadingReports, setLoadingReports] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  const fetchReports = useCallback(async () => {
    try {
      const { data } = await api.get('/api/reports/history');
      setReports(data);
    } catch {
      showToast('Failed to load reports', 'error');
    } finally {
      setLoadingReports(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const handleSelectReport = async (reportId) => {
    if (selectedId === reportId) return;
    setSelectedId(reportId);
    setSelectedReport(null);
    setLoadingDetail(true);
    try {
      const { data } = await api.get(`/api/reports/${reportId}`);
      setSelectedReport(data);
    } catch {
      showToast('Failed to load report detail', 'error');
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleGenerateDiet = async () => {
    if (!selectedId) return;
    setGenerating(true);
    try {
      await api.post(`/api/diet/generate/${selectedId}`);
      showToast('Diet plan generated!');
      // Refresh detail
      const { data } = await api.get(`/api/reports/${selectedId}`);
      setSelectedReport(data);
      await fetchReports();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to generate diet plan', 'error');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h2>Your Health Dashboard</h2>
          <p className="dashboard-sub">Welcome back, <strong>{user.name}</strong></p>
        </div>
        <div className="dashboard-stats">
          <div className="stat-chip">
            <span className="stat-num">{reports.length}</span>
            <span className="stat-label">Reports</span>
          </div>
          <div className="stat-chip">
            <span className="stat-num">{reports.filter((r) => r.diet_plan_id).length}</span>
            <span className="stat-label">Diet Plans</span>
          </div>
        </div>
      </div>

      {loadingReports ? (
        <div className="loading">
          <div className="spinner" />
          <p>Loading your reports...</p>
        </div>
      ) : (
        <div className="dashboard-body">
          <section className="section">
            <h3 className="section-title">Report History</h3>
            <ReportHistoryTable
              reports={reports}
              selectedId={selectedId}
              onSelect={handleSelectReport}
            />
          </section>

          {selectedId && (
            <section className="section">
              <h3 className="section-title">
                Report Details
                {loadingDetail && <span className="spinner-sm" style={{ marginLeft: 8 }} />}
              </h3>
              {loadingDetail ? (
                <div className="loading">
                  <div className="spinner" />
                </div>
              ) : (
                <ReportDetailPanel
                  report={selectedReport}
                  onGenerateDiet={handleGenerateDiet}
                  generating={generating}
                />
              )}
            </section>
          )}
        </div>
      )}

      {toast && (
        <div className={`toast ${toast.type}`}>
          {toast.type === 'success' ? '✓' : '✕'} {toast.message}
        </div>
      )}
    </div>
  );
}
