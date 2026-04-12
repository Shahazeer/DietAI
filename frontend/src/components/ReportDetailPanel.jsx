import { useState } from 'react';
import LabDataTable from './LabDataTable';

const MEALS = ['breakfast', 'lunch', 'dinner', 'snacks'];

function DietDayCard({ day }) {
  return (
    <div className="diet-day-card">
      <div className="diet-day-header">{day.day}</div>
      {MEALS.map((meal) => {
        const m = day[meal];
        if (!m) return null;
        return (
          <div key={meal} className="diet-meal">
            <span className="meal-label">{meal}</span>
            <span className="meal-name">{m.name}</span>
            {m.benefits?.length > 0 && (
              <div className="meal-benefits">
                {m.benefits.slice(0, 3).map((b, i) => (
                  <span key={i} className="benefit-pill">{b}</span>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function ReportDetailPanel({ report, onGenerateDiet, generating }) {
  const [tab, setTab] = useState('labs');

  if (!report) return null;

  const dietPlan = report.diet_plan;
  const hasDiet = dietPlan && dietPlan.days?.length > 0;
  const analysis = report.health_analysis || {};

  return (
    <div className="detail-panel">
      <div className="detail-tabs">
        <button
          className={`detail-tab ${tab === 'labs' ? 'active' : ''}`}
          onClick={() => setTab('labs')}
        >
          Lab Results
        </button>
        <button
          className={`detail-tab ${tab === 'diet' ? 'active' : ''}`}
          onClick={() => setTab('diet')}
        >
          Diet Plan
        </button>
        {analysis.issues?.length > 0 && (
          <button
            className={`detail-tab ${tab === 'analysis' ? 'active' : ''}`}
            onClick={() => setTab('analysis')}
          >
            Analysis
          </button>
        )}
      </div>

      <div className="detail-content">
        {tab === 'labs' && (
          <LabDataTable extractedData={report.extracted_data} />
        )}

        {tab === 'diet' && (
          <div>
            {!hasDiet ? (
              <div className="generate-prompt">
                <p>No diet plan generated yet.</p>
                <button
                  className="btn btn-primary"
                  onClick={onGenerateDiet}
                  disabled={generating}
                >
                  {generating
                    ? <><span className="spinner-sm" /> Generating...</>
                    : 'Generate 7-Day Diet Plan'}
                </button>
                {generating && (
                  <p className="generate-hint">
                    The AI is building your personalized plan — this may take 1–2 minutes.
                  </p>
                )}
              </div>
            ) : (
              <div className="diet-grid">
                {dietPlan.days.map((day, i) => (
                  <DietDayCard key={i} day={day} />
                ))}
              </div>
            )}
          </div>
        )}

        {tab === 'analysis' && (
          <div className="analysis-content">
            {analysis.issues?.length > 0 && (
              <section className="analysis-section">
                <h4>Health Issues</h4>
                <ul className="analysis-list issues">
                  {analysis.issues.map((issue, i) => (
                    <li key={i}>{issue}</li>
                  ))}
                </ul>
              </section>
            )}
            {analysis.risk_factors?.length > 0 && (
              <section className="analysis-section">
                <h4>Risk Factors</h4>
                <ul className="analysis-list risks">
                  {analysis.risk_factors.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </section>
            )}
            {analysis.recommendations?.length > 0 && (
              <section className="analysis-section">
                <h4>Recommendations</h4>
                <ul className="analysis-list recs">
                  {analysis.recommendations.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
