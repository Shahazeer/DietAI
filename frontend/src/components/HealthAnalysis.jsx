export default function HealthAnalysis({ data }) {
  if (!data) return null;

  const { extracted_data, health_analysis } = data;

  const getStatusColor = (status) => {
    switch (status) {
      case 'high': return 'var(--accent-red)';
      case 'low': return 'var(--accent-orange)';
      case 'normal': return 'var(--accent-green)';
      default: return 'var(--text-secondary)';
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'high': return 'danger';
      case 'low': return 'warning';
      case 'normal': return 'success';
      default: return '';
    }
  };

  return (
    <div className="card">
      <h2 className="card-title">🔬 Lab Report Analysis</h2>

      {/* Extracted Values */}
      <h3 style={{ margin: '1rem 0', color: 'var(--accent-cyan)' }}>
        📊 Extracted Values
      </h3>
      <div className="health-grid">
        {Object.entries(extracted_data || {}).map(([key, value]) => (
          <div 
            key={key} 
            className={`health-item ${getStatusClass(value.status)}`}
          >
            <div className="health-label">
              {key.replace(/_/g, ' ').toUpperCase()}
            </div>
            <div 
              className="health-value"
              style={{ color: getStatusColor(value.status) }}
            >
              {value.value} {value.unit}
            </div>
            {value.reference_range && (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Reference: {value.reference_range}
              </div>
            )}
            {value.status && (
              <div style={{ 
                fontSize: '0.75rem', 
                marginTop: '0.25rem',
                color: getStatusColor(value.status),
                textTransform: 'uppercase',
                fontWeight: 600
              }}>
                {value.status}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Health Issues */}
      {health_analysis?.issues?.length > 0 && (
        <>
          <h3 style={{ margin: '1.5rem 0 1rem', color: 'var(--accent-red)' }}>
            ⚠️ Health Issues Identified
          </h3>
          <ul style={{ paddingLeft: '1.5rem' }}>
            {health_analysis.issues.map((issue, index) => (
              <li key={index} style={{ marginBottom: '0.5rem', color: 'var(--accent-red)' }}>
                {issue}
              </li>
            ))}
          </ul>
        </>
      )}

      {/* Risk Factors */}
      {health_analysis?.risk_factors?.length > 0 && (
        <>
          <h3 style={{ margin: '1.5rem 0 1rem', color: 'var(--accent-orange)' }}>
            🔍 Risk Factors
          </h3>
          <ul style={{ paddingLeft: '1.5rem' }}>
            {health_analysis.risk_factors.map((risk, index) => (
              <li key={index} style={{ marginBottom: '0.5rem', color: 'var(--accent-orange)' }}>
                {risk}
              </li>
            ))}
          </ul>
        </>
      )}

      {/* Recommendations */}
      {health_analysis?.recommendations?.length > 0 && (
        <>
          <h3 style={{ margin: '1.5rem 0 1rem', color: 'var(--accent-green)' }}>
            💡 Recommendations
          </h3>
          <ul style={{ paddingLeft: '1.5rem' }}>
            {health_analysis.recommendations.map((rec, index) => (
              <li key={index} style={{ marginBottom: '0.5rem', color: 'var(--accent-green)' }}>
                {rec}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
