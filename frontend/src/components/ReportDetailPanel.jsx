import { useState } from 'react';
import LabDataTable from './LabDataTable';

const MEALS = ['breakfast', 'lunch', 'dinner', 'snacks'];

const MEAL_ICONS = {
  breakfast: '☀️',
  lunch: '🕛',
  dinner: '🌙',
  snacks: '🍎',
};

function DietDayCard({ day }) {
  return (
    <div className="diet-day-card">
      <div className="day-header">
        <span className="day-label">{day.day}</span>
      </div>
      <div className="day-meals">
        {MEALS.map((meal) => {
          const m = day[meal];
          if (!m) return null;
          return (
            <div key={meal} className="meal-block">
              <div className="meal-type-label">
                <span>{MEAL_ICONS[meal]}</span>
                <span>{meal.charAt(0).toUpperCase() + meal.slice(1)}</span>
              </div>
              <p className="meal-name">{m.name}</p>
              {m.benefits?.length > 0 && (
                <div className="meal-benefits">
                  {m.benefits.slice(0, 3).map((b) => (
                    <span key={b} className="meal-benefit-pill">{b}</span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AnalysisSection({ analysis }) {
  return (
    <div className="analysis-content">
      {analysis.issues?.length > 0 && (
        <div className="analysis-section">
          <h4 className="analysis-section-title danger">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            Health Issues
          </h4>
          <ul className="analysis-list issues">
            {analysis.issues.map((issue) => <li key={issue}>{issue}</li>)}
          </ul>
        </div>
      )}

      {analysis.risk_factors?.length > 0 && (
        <div className="analysis-section">
          <h4 className="analysis-section-title warn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
            Risk Factors
          </h4>
          <ul className="analysis-list risks">
            {analysis.risk_factors.map((r) => <li key={r}>{r}</li>)}
          </ul>
        </div>
      )}

      {analysis.recommendations?.length > 0 && (
        <div className="analysis-section">
          <h4 className="analysis-section-title good">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            Recommendations
          </h4>
          <ul className="analysis-list recs">
            {analysis.recommendations.map((r) => <li key={r}>{r}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function ReportDetailPanel({ report, onGenerateDiet, generating }) {
  const [tab, setTab] = useState('labs');

  if (!report) return null;

  const dietPlan = report.diet_plan;
  const hasDiet = dietPlan && dietPlan.days?.length > 0;
  const analysis = report.health_analysis || {};
  const hasAnalysis = (analysis.issues?.length ?? 0) + (analysis.risk_factors?.length ?? 0) + (analysis.recommendations?.length ?? 0) > 0;

  const tabs = [
    { key: 'labs', label: 'Lab Results' },
    { key: 'diet', label: 'Diet Plan' },
    ...(hasAnalysis ? [{ key: 'analysis', label: 'Analysis' }] : []),
  ];

  return (
    <div className="detail-panel">
      <div className="detail-tabs" role="tablist">
        {tabs.map((t) => (
          <button
            key={t.key}
            role="tab"
            aria-selected={tab === t.key}
            className={`detail-tab${tab === t.key ? ' active' : ''}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="detail-content" role="tabpanel">
        {tab === 'labs' && (
          <LabDataTable extractedData={report.extracted_data} />
        )}

        {tab === 'diet' && (
          hasDiet ? (
            <div className="diet-grid">
              {dietPlan.days.map((day) => (
                <DietDayCard key={day.day} day={day} />
              ))}
            </div>
          ) : (
            <div className="detail-generate">
              <div className="detail-generate-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2" />
                  <path d="M7 2v20" />
                  <path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7" />
                </svg>
              </div>
              <h3>No diet plan yet</h3>
              <p>Generate a 7-day meal plan personalised to the biomarkers in this report.</p>
              <button
                className="btn btn-primary"
                onClick={onGenerateDiet}
                disabled={generating}
                style={{ marginTop: '1rem' }}
              >
                {generating ? (
                  <><span className="spinner-sm" /> Generating plan…</>
                ) : (
                  'Generate 7-Day Diet Plan'
                )}
              </button>
              {generating && (
                <p className="generate-hint">
                  The AI is building your personalised plan — this may take 1–2 minutes.
                </p>
              )}
            </div>
          )
        )}

        {tab === 'analysis' && <AnalysisSection analysis={analysis} />}
      </div>
    </div>
  );
}
