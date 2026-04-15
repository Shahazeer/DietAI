import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
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
          <h2 className="auth-panel-title">Your health, <br />personalised.</h2>
          <p className="auth-panel-sub">
            Upload lab reports. Get AI-powered nutrition plans tailored to your biomarkers.
          </p>
        </div>

        <div className="auth-deco-cards">
          <div className="auth-deco-card">
            <div className="auth-deco-icon green">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <div>
              <div className="auth-deco-label">Glucose</div>
              <div className="auth-deco-val">92 mg/dL <span className="tag-good">Normal</span></div>
            </div>
          </div>
          <div className="auth-deco-card">
            <div className="auth-deco-icon amber">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19" />
                <polyline points="19 12 12 19 5 12" />
              </svg>
            </div>
            <div>
              <div className="auth-deco-label">Vitamin D</div>
              <div className="auth-deco-val">18 ng/mL <span className="tag-warn">Low</span></div>
            </div>
          </div>
          <div className="auth-deco-card">
            <div className="auth-deco-icon blue">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
            </div>
            <div>
              <div className="auth-deco-label">7-Day Plan</div>
              <div className="auth-deco-val">AI Generated <span className="tag-good">Ready</span></div>
            </div>
          </div>
        </div>
      </div>

      {/* Right form side */}
      <div className="auth-form-side">
        <div className="auth-form-wrap">
          <div className="auth-form-header">
            <h1>Welcome back</h1>
            <p>Sign in to continue your health journey</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form" noValidate>
            {error && <div className="auth-error" role="alert">{error}</div>}

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

            <div className="form-group">
              <label className="form-label" htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                name="password"
                className="form-input"
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
                autoComplete="current-password"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? (
                <><span className="spinner-sm" /> Signing in...</>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          <p className="auth-footer-link">
            No account? <Link to="/register">Create one free</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
