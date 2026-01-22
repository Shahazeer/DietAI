import { useState } from 'react';

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const MEAL_ICONS = {
  breakfast: '🌅',
  morning_snack: '🍎',
  lunch: '🌞',
  evening_snack: '☕',
  dinner: '🌙',
};

export default function DietPlanView({ plan }) {
  const [selectedDay, setSelectedDay] = useState(0);

  if (!plan || !plan.days || plan.days.length === 0) {
    return (
      <div className="card">
        <h2 className="card-title">🍽️ Diet Plan</h2>
        <div className="empty-state">
          <div className="empty-state-icon">⚠️</div>
          <p style={{ color: 'var(--accent-orange)' }}>
            {plan?.rationale || 'No diet plan generated yet.'}
          </p>
          <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
            The AI model may have produced an incomplete response. Try generating again.
          </p>
        </div>
      </div>
    );
  }

  const MealCard = ({ type, meal }) => {
    if (!meal) return null;
    
    return (
      <div style={{
        background: 'var(--bg-tertiary)',
        borderRadius: '8px',
        padding: '1rem',
        marginBottom: '1rem'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem',
          marginBottom: '0.5rem'
        }}>
          <span style={{ fontSize: '1.5rem' }}>{MEAL_ICONS[type]}</span>
          <span style={{ 
            textTransform: 'capitalize',
            color: 'var(--text-secondary)',
            fontSize: '0.85rem'
          }}>
            {type.replace('_', ' ')}
          </span>
        </div>
        <h4 style={{ marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
          {meal.name}
        </h4>
        {meal.calories && (
          <div style={{ 
            fontSize: '0.8rem', 
            color: 'var(--accent-orange)',
            marginBottom: '0.5rem'
          }}>
            🔥 {meal.calories} cal
          </div>
        )}
        {meal.ingredients && meal.ingredients.length > 0 && (
          <div style={{ marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Ingredients:
            </span>
            <div className="tags" style={{ marginTop: '0.25rem' }}>
              {meal.ingredients.map((ing, idx) => (
                <span key={idx} className="tag" style={{ fontSize: '0.75rem' }}>
                  {ing}
                </span>
              ))}
            </div>
          </div>
        )}
        {meal.benefits && meal.benefits.length > 0 && (
          <div className="meal-benefits">
            {meal.benefits.map((benefit, idx) => (
              <span key={idx} className="benefit-tag">
                ✓ {benefit}
              </span>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="card">
      <h2 className="card-title">🍽️ Your 7-Day Diet Plan</h2>
      
      {/* Rationale */}
      {plan.rationale && (
        <div style={{
          background: 'rgba(88, 166, 255, 0.1)',
          border: '1px solid var(--accent-blue)',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '1.5rem'
        }}>
          <div style={{ fontWeight: 600, marginBottom: '0.5rem', color: 'var(--accent-blue)' }}>
            💡 Plan Rationale
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            {plan.rationale}
          </p>
        </div>
      )}

      {/* Progress Report */}
      {plan.progress_report && (
        <div style={{
          background: 'var(--bg-tertiary)',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '1.5rem'
        }}>
          <div style={{ fontWeight: 600, marginBottom: '0.5rem', color: 'var(--accent-purple)' }}>
            📈 Progress from Previous Plan
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <div style={{ flex: 1 }}>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${plan.progress_report.effectiveness_score}%` }}
                />
              </div>
            </div>
            <div style={{ 
              fontSize: '1.5rem', 
              fontWeight: 700, 
              color: 'var(--accent-green)' 
            }}>
              {plan.progress_report.effectiveness_score}%
            </div>
          </div>
          {plan.progress_report.improvements?.length > 0 && (
            <div style={{ marginBottom: '0.5rem' }}>
              <span style={{ color: 'var(--accent-green)' }}>✓ Improvements: </span>
              <span style={{ color: 'var(--text-secondary)' }}>
                {plan.progress_report.improvements.join(', ')}
              </span>
            </div>
          )}
          {plan.progress_report.current_issues?.length > 0 && (
            <div>
              <span style={{ color: 'var(--accent-orange)' }}>⚠ Still needs work: </span>
              <span style={{ color: 'var(--text-secondary)' }}>
                {plan.progress_report.current_issues.join(', ')}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Day Tabs */}
      <div style={{ 
        display: 'flex', 
        gap: '0.5rem',
        marginBottom: '1.5rem',
        overflowX: 'auto',
        paddingBottom: '0.5rem'
      }}>
        {plan.days.map((day, index) => (
          <button
            key={index}
            className={`nav-tab ${selectedDay === index ? 'active' : ''}`}
            onClick={() => setSelectedDay(index)}
            style={{ whiteSpace: 'nowrap' }}
          >
            {DAY_NAMES[index] || `Day ${day.day}`}
          </button>
        ))}
      </div>

      {/* Selected Day Meals */}
      {plan.days[selectedDay] && (
        <div>
          <MealCard type="breakfast" meal={plan.days[selectedDay].breakfast} />
          <MealCard type="morning_snack" meal={plan.days[selectedDay].morning_snack} />
          <MealCard type="lunch" meal={plan.days[selectedDay].lunch} />
          <MealCard type="evening_snack" meal={plan.days[selectedDay].evening_snack} />
          <MealCard type="dinner" meal={plan.days[selectedDay].dinner} />
        </div>
      )}
    </div>
  );
}
