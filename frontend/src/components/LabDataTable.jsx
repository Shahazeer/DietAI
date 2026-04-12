function getStatusClass(value, ref_range) {
  if (!ref_range || !value) return '';
  const match = ref_range.match(/([\d.]+)\s*[-–]\s*([\d.]+)/);
  if (!match) return '';
  const [, low, high] = match;
  const num = parseFloat(value);
  if (isNaN(num)) return '';
  if (num < parseFloat(low) || num > parseFloat(high)) return 'flag';
  return 'normal';
}

export default function LabDataTable({ extractedData }) {
  if (!extractedData || Object.keys(extractedData).length === 0) {
    return <p className="empty-text">No lab values extracted.</p>;
  }

  const rows = Object.entries(extractedData).map(([key, item]) => {
    const status = getStatusClass(item.value, item.reference_range);
    return { key, ...item, status };
  });

  const flagged = rows.filter((r) => r.status === 'flag');
  const normal = rows.filter((r) => r.status !== 'flag');
  const ordered = [...flagged, ...normal];

  return (
    <div className="lab-table-wrap">
      <table className="lab-table">
        <thead>
          <tr>
            <th>Test</th>
            <th>Value</th>
            <th>Unit</th>
            <th>Reference Range</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {ordered.map((row) => (
            <tr key={row.key} className={`lab-row ${row.status}`}>
              <td className="test-name">{row.test_name || row.key}</td>
              <td className="test-value">
                <span className={row.status === 'flag' ? 'value-flag' : ''}>
                  {row.value ?? '—'}
                </span>
              </td>
              <td className="test-unit">{row.unit || '—'}</td>
              <td className="test-ref">{row.reference_range || '—'}</td>
              <td>
                {row.status === 'flag' ? (
                  <span className="status-badge warn">Abnormal</span>
                ) : row.status === 'normal' ? (
                  <span className="status-badge good">Normal</span>
                ) : (
                  <span className="status-badge neutral">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
