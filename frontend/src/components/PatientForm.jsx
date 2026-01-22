import { useState } from 'react';

export default function PatientForm({ onPatientCreated }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    gender: '',
    dietary_preference: {
      type: 'non-veg',
      allergies: [],
      cuisines: ['Indian'],
      meal_frequency: 3,
    },
  });
  const [allergyInput, setAllergyInput] = useState('');
  const [cuisineInput, setCuisineInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePreferenceChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      dietary_preference: {
        ...prev.dietary_preference,
        [name]: name === 'meal_frequency' ? parseInt(value) : value,
      },
    }));
  };

  const addAllergy = () => {
    if (allergyInput.trim()) {
      setFormData((prev) => ({
        ...prev,
        dietary_preference: {
          ...prev.dietary_preference,
          allergies: [...prev.dietary_preference.allergies, allergyInput.trim()],
        },
      }));
      setAllergyInput('');
    }
  };

  const removeAllergy = (index) => {
    setFormData((prev) => ({
      ...prev,
      dietary_preference: {
        ...prev.dietary_preference,
        allergies: prev.dietary_preference.allergies.filter((_, i) => i !== index),
      },
    }));
  };

  const addCuisine = () => {
    if (cuisineInput.trim()) {
      setFormData((prev) => ({
        ...prev,
        dietary_preference: {
          ...prev.dietary_preference,
          cuisines: [...prev.dietary_preference.cuisines, cuisineInput.trim()],
        },
      }));
      setCuisineInput('');
    }
  };

  const removeCuisine = (index) => {
    setFormData((prev) => ({
      ...prev,
      dietary_preference: {
        ...prev.dietary_preference,
        cuisines: prev.dietary_preference.cuisines.filter((_, i) => i !== index),
      },
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/patients/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create patient');
      }

      const patient = await response.json();
      onPatientCreated(patient);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="card-title">👤 Register New Patient</h2>
      
      {error && (
        <div style={{ 
          background: 'rgba(248, 81, 73, 0.1)', 
          border: '1px solid var(--accent-red)',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '1rem',
          color: 'var(--accent-red)'
        }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Full Name *</label>
            <input
              type="text"
              name="name"
              className="form-input"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Enter patient's full name"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Email *</label>
            <input
              type="email"
              name="email"
              className="form-input"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="patient@example.com"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Phone</label>
            <input
              type="tel"
              name="phone"
              className="form-input"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+91 98765 43210"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Gender</label>
            <select
              name="gender"
              className="form-select"
              value={formData.gender}
              onChange={handleChange}
            >
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <h3 style={{ margin: '1.5rem 0 1rem', color: 'var(--accent-purple)' }}>
          🥗 Dietary Preferences
        </h3>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Diet Type *</label>
            <select
              name="type"
              className="form-select"
              value={formData.dietary_preference.type}
              onChange={handlePreferenceChange}
            >
              <option value="veg">Vegetarian</option>
              <option value="non-veg">Non-Vegetarian</option>
              <option value="vegan">Vegan</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Meals per Day</label>
            <select
              name="meal_frequency"
              className="form-select"
              value={formData.dietary_preference.meal_frequency}
              onChange={handlePreferenceChange}
            >
              <option value={3}>3 meals</option>
              <option value={4}>4 meals</option>
              <option value={5}>5 meals</option>
              <option value={6}>6 meals</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Allergies</label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              className="form-input"
              value={allergyInput}
              onChange={(e) => setAllergyInput(e.target.value)}
              placeholder="Add allergy (e.g., peanuts)"
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAllergy())}
            />
            <button type="button" className="btn btn-secondary" onClick={addAllergy}>
              Add
            </button>
          </div>
          <div className="tags">
            {formData.dietary_preference.allergies.map((allergy, index) => (
              <span key={index} className="tag">
                {allergy}
                <span className="tag-remove" onClick={() => removeAllergy(index)}>✕</span>
              </span>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Preferred Cuisines</label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              className="form-input"
              value={cuisineInput}
              onChange={(e) => setCuisineInput(e.target.value)}
              placeholder="Add cuisine (e.g., Mediterranean)"
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCuisine())}
            />
            <button type="button" className="btn btn-secondary" onClick={addCuisine}>
              Add
            </button>
          </div>
          <div className="tags">
            {formData.dietary_preference.cuisines.map((cuisine, index) => (
              <span key={index} className="tag">
                {cuisine}
                <span className="tag-remove" onClick={() => removeCuisine(index)}>✕</span>
              </span>
            ))}
          </div>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner" style={{ width: 20, height: 20 }}></span>
              Creating...
            </>
          ) : (
            <>✨ Register Patient</>
          )}
        </button>
      </form>
    </div>
  );
}
