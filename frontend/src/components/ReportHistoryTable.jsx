function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

const TrashIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
    <path d="M10 11v6M14 11v6" />
    <path d="M9 6V4h6v2" />
  </svg>
);

export default function ReportHistoryTable({ reports, selectedId, onSelect, onDelete, deletingId }) {
  if (!reports.length) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
          </svg>
        </div>
        <h3>No reports yet</h3>
        <p>Upload your first lab report to get started.</p>
      </div>
    );
  }

  return (
    <div className="report-list">
      {reports.map((r) => (
        <div
          key={r.id}
          className={`report-card${selectedId === r.id ? ' selected' : ''}`}
          onClick={() => onSelect(r.id)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && onSelect(r.id)}
        >
          {/* File icon */}
          <div className="report-card-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
          </div>

          {/* Body: name/date + pills */}
          <div className="report-card-body">
            <div className="report-card-top-row">
              <span className="report-card-name">{r.filename}</span>
              <span className="report-card-date">{formatDate(r.upload_date)}</span>
            </div>
            <div className="report-card-pills">
              <span className="report-pill neutral">
                {r.test_count} test{r.test_count !== 1 ? 's' : ''}
              </span>
              {r.issues?.length === 0 ? (
                <span className="report-pill good">All normal</span>
              ) : (
                <span className="report-pill warn">
                  {r.issues.length} flag{r.issues.length > 1 ? 's' : ''}
                </span>
              )}
              {r.diet_plan_id ? (
                <span className="report-pill good">Plan ready</span>
              ) : (
                <span className="report-pill neutral">No plan</span>
              )}
            </div>
          </div>

          {/* Delete button */}
          <button
            className={`report-card-delete${deletingId === r.id ? ' deleting' : ''}`}
            onClick={(e) => onDelete(e, r.id)}
            disabled={deletingId === r.id}
            aria-label="Delete report"
            title="Delete report"
          >
            {deletingId === r.id ? <span className="spinner-sm" /> : <TrashIcon />}
          </button>
        </div>
      ))}
    </div>
  );
}
