import { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ALLERGENS = ['Gluten', 'Dairy', 'Nuts', 'Shellfish', 'Eggs', 'Soy', 'Fish'];

function passwordStrength(password) {
  if (!password) return { score: 0, label: '', checks: [] };
  const checks = [
    { pass: password.length >= 8, label: 'At least 8 characters' },
    { pass: /[A-Z]/.test(password), label: 'One uppercase letter' },
    { pass: /[0-9]/.test(password), label: 'One number' },
    { pass: /[^A-Za-z0-9]/.test(password), label: 'One special character' },
  ];
  const score = checks.filter((c) => c.pass).length;
  const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
  return { score, label: labels[score], checks };
}

export default function RegisterPage() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    age: '',
    gender: '',
    dietary_preferences: 'non-veg',
    allergies: [],
  });
  const strength = useMemo(() => passwordStrength(form.password), [form.password]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const toggleAllergen = (allergen) => {
    setForm((f) => ({
      ...f,
      allergies: f.allergies.includes(allergen)
        ? f.allergies.filter((a) => a !== allergen)
        : [...f.allergies, allergen],
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register({ ...form, age: parseInt(form.age, 10) });
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split">
      {/* Left decorative panel */}
      <div className="auth-panel">
        <div className="auth-panel-brand">
          <div className="auth-panel-logo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <span>Dietician AI</span>
        </div>

        <div className="auth-panel-copy">
          <h2 className="auth-panel-title">Science-backed nutrition, <br />built for you.</h2>
          <p className="auth-panel-sub">
            Connect your lab results to a 7-day meal plan that adapts to your unique biomarkers.
          </p>
        </div>

        <div className="auth-feature-list">
          {[
            { icon: '🔬', title: 'Lab-driven plans', desc: 'Meals calibrated to your actual blood work' },
            { icon: '🥗', title: 'Dietary-aware', desc: 'Respects allergies and preferences' },
            { icon: '📈', title: 'Track progress', desc: 'Compare reports over time' },
          ].map((f) => (
            <div key={f.title} className="auth-feature-item">
              <span className="auth-feature-icon">{f.icon}</span>
              <div>
                <div className="auth-feature-title">{f.title}</div>
                <div className="auth-feature-desc">{f.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right form side */}
      <div className="auth-form-side auth-form-side-scroll">
        <div className="auth-form-wrap">
          <div className="auth-form-header">
            <h1>Create your account</h1>
            <p>Start your personalised diet journey today</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form" noValidate>
            {error && <div className="auth-error" role="alert">{error}</div>}

            <div className="form-row">
              <div className="form-group">
                <label className="form-label" htmlFor="name">Full name</label>
                <input
                  id="name"
                  type="text"
                  name="name"
                  className="form-input"
                  placeholder="Jane Smith"
                  value={form.name}
                  onChange={handleChange}
                  autoComplete="name"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="email">Email address</label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  className="form-input"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={handleChange}
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label" htmlFor="age">Age</label>
                <input
                  id="age"
                  type="number"
                  name="age"
                  className="form-input"
                  placeholder="35"
                  min="1"
                  max="120"
                  value={form.age}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="gender">Gender</label>
                <select
                  id="gender"
                  name="gender"
                  className="form-select"
                  value={form.gender}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="dietary_preferences">Dietary preference</label>
              <select
                id="dietary_preferences"
                name="dietary_preferences"
                className="form-select"
                value={form.dietary_preferences}
                onChange={handleChange}
              >
                <option value="non-veg">Non-vegetarian</option>
                <option value="vegetarian">Vegetarian</option>
                <option value="eggetarian">Eggetarian (eggs, no meat)</option>
                <option value="vegan">Vegan</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Allergies / intolerances</label>
              <div className="allergen-grid">
                {ALLERGENS.map((a) => (
                  <button
                    key={a}
                    type="button"
                    className={`allergen-chip${form.allergies.includes(a) ? ' selected' : ''}`}
                    onClick={() => toggleAllergen(a)}
                  >
                    {a}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                name="password"
                className="form-input"
                placeholder="Min. 8 characters"
                value={form.password}
                onChange={handleChange}
                autoComplete="new-password"
                minLength={8}
                required
              />
              {form.password && (
                <div className="password-strength">
                  <div className="strength-bar">
                    {[1, 2, 3, 4].map((i) => (
                      <div
                        key={i}
                        className={`strength-segment${i <= strength.score ? ` s${strength.score}` : ''}`}
                      />
                    ))}
                  </div>
                  <span className={`strength-label s${strength.score}`}>{strength.label}</span>
                  <ul className="strength-checks">
                    {strength.checks.map((c) => (
                      <li key={c.label} className={c.pass ? 'pass' : 'fail'}>
                        {c.pass ? '✓' : '✗'} {c.label}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? (
                <><span className="spinner-sm" /> Creating account...</>
              ) : (
                'Create account'
              )}
            </button>
          </form>

          <p className="auth-footer-link">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
