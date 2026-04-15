import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import ReportHistoryTable from '../components/ReportHistoryTable';
import ReportDetailPanel from '../components/ReportDetailPanel';

const PAGE_SIZE = 10;

function StatCard({ label, value, icon, colorClass }) {
  return (
    <div className={`stat-card ${colorClass}`}>
      <div className="stat-icon-wrap">{icon}</div>
      <div className="stat-body">
        <span className="stat-value">{value}</span>
        <span className="stat-label">{label}</span>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loadingReports, setLoadingReports] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  const fetchReports = useCallback(async (targetPage = 1) => {
    setLoadingReports(true);
    try {
      const { data } = await api.get('/api/reports/history', {
        params: { page: targetPage, limit: PAGE_SIZE },
      });
      setReports(data);
      setHasMore(data.length === PAGE_SIZE);
      setPage(targetPage);
    } catch {
      showToast('Failed to load reports', 'error');
    } finally {
      setLoadingReports(false);
    }
  }, []);

  useEffect(() => {
    fetchReports(1);
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
      const { data } = await api.get(`/api/reports/${selectedId}`);
      setSelectedReport(data);
      await fetchReports(page);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to generate diet plan', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleDeleteReport = async (e, reportId) => {
    e.stopPropagation();
    if (!window.confirm('Delete this report and its diet plan permanently?')) return;
    setDeletingId(reportId);
    try {
      await api.delete(`/api/reports/${reportId}`);
      showToast('Report deleted');
      if (selectedId === reportId) {
        setSelectedId(null);
        setSelectedReport(null);
      }
      await fetchReports(page);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to delete report', 'error');
    } finally {
      setDeletingId(null);
    }
  };

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  const totalReports = reports.length;
  const plansGenerated = reports.filter((r) => r.diet_plan_id).length;
  const totalIssues = reports.reduce((sum, r) => sum + (r.issues?.length ?? 0), 0);

  return (
    <div className="page-wrap">
      {/* Greeting banner */}
      <header className="dash-greeting">
        <div className="dash-greeting-text">
          <h1>{greeting}, {user?.name?.split(' ')[0]}.</h1>
          <p>Here's a summary of your health data.</p>
        </div>
        <Link to="/new-report" className="btn btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '6px' }}>
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          New Report
        </Link>
      </header>

      {/* Stat cards */}
      <div className="dash-stats">
        <StatCard
          label="Reports uploaded"
          value={totalReports}
          colorClass="stat-green"
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
          }
        />
        <StatCard
          label="Diet plans generated"
          value={plansGenerated}
          colorClass="stat-orange"
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2" />
              <path d="M7 2v20" />
              <path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7" />
            </svg>
          }
        />
        <StatCard
          label="Health flags"
          value={totalIssues}
          colorClass="stat-blue"
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          }
        />
      </div>

      {/* Main content */}
      <div className="dash-body">
        {/* Report history */}
        <section className="section-card">
          <div className="section-card-header">
            <h2 className="section-card-title">Report History</h2>
            {(page > 1 || hasMore) && (
              <div className="pagination">
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => fetchReports(page - 1)}
                  disabled={page === 1}
                >
                  ← Prev
                </button>
                <span className="page-indicator">Page {page}</span>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => fetchReports(page + 1)}
                  disabled={!hasMore}
                >
                  Next →
                </button>
              </div>
            )}
          </div>

          {loadingReports ? (
            <div className="loading-state">
              <div className="spinner" />
              <p>Loading your reports…</p>
            </div>
          ) : (
            <ReportHistoryTable
              reports={reports}
              selectedId={selectedId}
              onSelect={handleSelectReport}
              onDelete={handleDeleteReport}
              deletingId={deletingId}
            />
          )}
        </section>

        {/* Detail panel */}
        {selectedId && (
          <section className="section-card">
            <div className="section-card-header">
              <h2 className="section-card-title">Report Details</h2>
              {loadingDetail && <span className="spinner-sm" />}
            </div>
            {loadingDetail ? (
              <div className="loading-state">
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

      {toast && (
        <div className={`toast ${toast.type}`} role="status" aria-live="polite">
          {toast.type === 'success' ? '✓' : '✕'} {toast.message}
        </div>
      )}
    </div>
  );
}
