export default function ReportHistoryTable({ reports, selectedId, onSelect }) {
  if (!reports.length) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📋</div>
        <h3>No reports yet</h3>
        <p>Upload your first lab report to get started.</p>
      </div>
    );
  }

  return (
    <div className="report-table-wrap">
      <table className="report-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>File</th>
            <th>Tests</th>
            <th>Issues</th>
            <th>Diet Plan</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((r) => (
            <tr
              key={r.id}
              className={`report-row ${selectedId === r.id ? 'selected' : ''}`}
              onClick={() => onSelect(r.id)}
            >
              <td className="report-date">
                {new Date(r.upload_date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </td>
              <td className="report-file">
                <span className="file-icon">📄</span>
                {r.filename}
              </td>
              <td className="report-tests">
                <span className="test-badge">{r.test_count}</span>
              </td>
              <td className="report-issues">
                {r.issues.length === 0 ? (
                  <span className="status-badge good">All Normal</span>
                ) : (
                  <span className="status-badge warn">{r.issues.length} Flag{r.issues.length > 1 ? 's' : ''}</span>
                )}
              </td>
              <td>
                {r.diet_plan_id ? (
                  <span className="status-badge good">Generated</span>
                ) : (
                  <span className="status-badge neutral">Pending</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
