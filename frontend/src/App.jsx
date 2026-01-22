import { useState, useEffect } from 'react';
import PatientForm from './components/PatientForm';
import LabReportUpload from './components/LabReportUpload';
import HealthAnalysis from './components/HealthAnalysis';
import DietPlanView from './components/DietPlanView';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('register');
  const [currentPatient, setCurrentPatient] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [dietPlan, setDietPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [patientEmail, setPatientEmail] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);

  // Load patient from localStorage on mount
  useEffect(() => {
    const savedPatient = localStorage.getItem('currentPatient');
    if (savedPatient) {
      try {
        const patient = JSON.parse(savedPatient);
        setCurrentPatient(patient);
        setActiveTab('upload');
      } catch (e) {
        localStorage.removeItem('currentPatient');
      }
    }
  }, []);

  // Save patient to localStorage when it changes
  useEffect(() => {
    if (currentPatient) {
      localStorage.setItem('currentPatient', JSON.stringify(currentPatient));
    } else {
      localStorage.removeItem('currentPatient');
    }
  }, [currentPatient]);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  const handlePatientCreated = (patient) => {
    setCurrentPatient(patient);
    showToast(`Patient "${patient.name}" registered successfully!`);
    setActiveTab('upload');
  };

  const handleReportUploaded = (data) => {
    setReportData(data);
    showToast('Lab report analyzed successfully!');
    setActiveTab('analysis');
  };

  const handleGenerateDietPlan = async () => {
    if (!reportData?.id) {
      showToast('Please upload a lab report first', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/diet/generate/${reportData.id}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to generate diet plan');
      }

      const plan = await response.json();
      setDietPlan(plan);
      showToast('Diet plan generated successfully!');
      setActiveTab('plan');
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchPatient = async (e) => {
    e.preventDefault();
    if (!patientEmail.trim()) {
      showToast('Please enter an email', 'error');
      return;
    }

    setSearchLoading(true);
    try {
      // Search for patient by email using a new endpoint
      const response = await fetch(`http://localhost:8000/api/patients/search?email=${encodeURIComponent(patientEmail)}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Patient not found with this email');
        }
        throw new Error('Failed to search patient');
      }

      const patient = await response.json();
      setCurrentPatient(patient);
      setPatientEmail('');
      showToast(`Welcome back, ${patient.name}!`);
      setActiveTab('upload');
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setSearchLoading(false);
    }
  };

  const handleClearPatient = () => {
    setCurrentPatient(null);
    setReportData(null);
    setDietPlan(null);
    setActiveTab('register');
    localStorage.removeItem('currentPatient');
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>🥗 Dietician Agent</h1>
        <p>AI-Powered Personalized Diet Planning</p>
      </header>

      {/* Patient Info Bar */}
      {currentPatient && (
        <div style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <span style={{ color: 'var(--text-secondary)' }}>Current Patient: </span>
            <span style={{ fontWeight: 600 }}>{currentPatient.name}</span>
            <span style={{ 
              marginLeft: '1rem',
              padding: '0.25rem 0.75rem',
              background: 'var(--accent-purple)',
              borderRadius: '20px',
              fontSize: '0.75rem'
            }}>
              {currentPatient.dietary_preference?.type || 'N/A'}
            </span>
          </div>
          <button 
            className="btn btn-secondary"
            onClick={handleClearPatient}
          >
            Switch Patient
          </button>
        </div>
      )}

      {/* Navigation Tabs */}
      <nav className="nav-tabs">
        <button
          className={`nav-tab ${activeTab === 'register' ? 'active' : ''}`}
          onClick={() => setActiveTab('register')}
        >
          👤 Register/Find
        </button>
        <button
          className={`nav-tab ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
          disabled={!currentPatient}
        >
          📄 Upload Report
        </button>
        <button
          className={`nav-tab ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
          disabled={!reportData}
        >
          🔬 Analysis
        </button>
        <button
          className={`nav-tab ${activeTab === 'plan' ? 'active' : ''}`}
          onClick={() => setActiveTab('plan')}
          disabled={!dietPlan}
        >
          🍽️ Diet Plan
        </button>
      </nav>

      {/* Content */}
      <main>
        {activeTab === 'register' && (
          <>
            {/* Find Existing Patient */}
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h2 className="card-title">🔍 Find Existing Patient</h2>
              <form onSubmit={handleSearchPatient} style={{ display: 'flex', gap: '1rem' }}>
                <input
                  type="email"
                  className="form-input"
                  placeholder="Enter patient's email..."
                  value={patientEmail}
                  onChange={(e) => setPatientEmail(e.target.value)}
                  style={{ flex: 1 }}
                />
                <button 
                  type="submit" 
                  className="btn btn-secondary"
                  disabled={searchLoading}
                >
                  {searchLoading ? 'Searching...' : 'Find Patient'}
                </button>
              </form>
            </div>

            {/* Or Register New */}
            <div style={{ 
              textAlign: 'center', 
              margin: '1.5rem 0', 
              color: 'var(--text-secondary)',
              position: 'relative'
            }}>
              <span style={{ 
                background: 'var(--bg-primary)', 
                padding: '0 1rem',
                position: 'relative',
                zIndex: 1
              }}>
                OR
              </span>
              <div style={{
                position: 'absolute',
                top: '50%',
                left: 0,
                right: 0,
                borderTop: '1px solid var(--border-color)'
              }} />
            </div>

            <PatientForm onPatientCreated={handlePatientCreated} />
          </>
        )}

        {activeTab === 'upload' && currentPatient && (
          <LabReportUpload
            patientId={currentPatient.id}
            onReportUploaded={handleReportUploaded}
          />
        )}

        {activeTab === 'analysis' && reportData && (
          <>
            <HealthAnalysis data={reportData} />
            <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
              <button
                className="btn btn-success"
                onClick={handleGenerateDietPlan}
                disabled={loading}
                style={{ padding: '1rem 2rem', fontSize: '1.1rem' }}
              >
                {loading ? (
                  <>
                    <span className="spinner" style={{ width: 20, height: 20 }}></span>
                    Generating with Ollama...
                  </>
                ) : (
                  <>🍽️ Generate 7-Day Diet Plan</>
                )}
              </button>
              {loading && (
                <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>
                  🦙 Ollama is creating your personalized meal plan. This may take a minute...
                </p>
              )}
            </div>
          </>
        )}

        {activeTab === 'plan' && (
          <DietPlanView plan={dietPlan} />
        )}
      </main>

      {/* Toast Notification */}
      {toast && (
        <div className={`toast ${toast.type}`}>
          {toast.type === 'success' ? '✓' : '✕'} {toast.message}
        </div>
      )}

      {/* Footer */}
      <footer style={{ 
        textAlign: 'center', 
        marginTop: '3rem', 
        color: 'var(--text-secondary)',
        fontSize: '0.9rem'
      }}>
        <p>Powered by Ollama • Running locally on your desktop</p>
        <p style={{ marginTop: '0.5rem', fontSize: '0.8rem' }}>
          ⚠️ This tool provides dietary suggestions only. Always consult a healthcare professional.
        </p>
      </footer>
    </div>
  );
}

export default App;
