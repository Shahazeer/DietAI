/**
 * Determines status class from a numeric value and a reference range string.
 * Handles formats: "X-Y", "X–Y", "<X", ">X", "<=X", ">=X"
 */
function getStatusClass(value, ref_range) {
  if (ref_range == null || value == null) return '';
  const num = parseFloat(value);
  if (isNaN(num)) return '';

  const ref = ref_range.trim();

  // Range: "70-100" or "70–100"
  const rangeMatch = ref.match(/^([\d.]+)\s*[-–]\s*([\d.]+)$/);
  if (rangeMatch) {
    const low = parseFloat(rangeMatch[1]);
    const high = parseFloat(rangeMatch[2]);
    return num < low || num > high ? 'flag' : 'normal';
  }

  // Upper bound: "<200" or "<=200"
  const ltMatch = ref.match(/^<=?\s*([\d.]+)$/);
  if (ltMatch) {
    return num > parseFloat(ltMatch[1]) ? 'flag' : 'normal';
  }

  // Lower bound: ">40" or ">=40"
  const gtMatch = ref.match(/^>=?\s*([\d.]+)$/);
  if (gtMatch) {
    return num < parseFloat(gtMatch[1]) ? 'flag' : 'normal';
  }

  return '';
}

export default function LabDataTable({ extractedData }) {
  if (!extractedData || Object.keys(extractedData).length === 0) {
    return <p className="empty-text">No lab values extracted.</p>;
  }

  const rows = Object.entries(extractedData).map(([key, item]) => {
    let status = getStatusClass(item.value, item.reference_range);
    // Fall back to model-provided status when ref range can't be parsed
    if (!status && item.status) {
      status = item.status === 'normal' ? 'normal' : item.status === 'unknown' ? '' : 'flag';
    }
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
