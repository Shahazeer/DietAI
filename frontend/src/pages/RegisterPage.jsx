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

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

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
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card auth-card-wide">
        <div className="auth-header">
          <div className="auth-icon">⚕</div>
          <h1>Create your account</h1>
          <p>Start your personalized diet journey</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="auth-error">{error}</div>}

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                name="name"
                className="form-input"
                placeholder="John Smith"
                value={form.name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                type="email"
                name="email"
                className="form-input"
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Age</label>
              <input
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
              <label className="form-label">Gender</label>
              <select
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
            <label className="form-label">Dietary Preferences</label>
            <select
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
            <label className="form-label">Allergies / Intolerances</label>
            <div className="allergen-grid">
              {ALLERGENS.map((a) => (
                <button
                  key={a}
                  type="button"
                  className={`allergen-chip ${form.allergies.includes(a) ? 'selected' : ''}`}
                  onClick={() => toggleAllergen(a)}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              className="form-input"
              placeholder="At least 8 characters"
              value={form.password}
              onChange={handleChange}
              minLength={8}
              required
            />
            {form.password && (
              <div className="password-strength">
                <div className="strength-bar">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className={`strength-segment ${i <= strength.score ? `s${strength.score}` : ''}`}
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
            {loading ? <><span className="spinner-sm" /> Creating account...</> : 'Create account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
