import { useState, useRef } from 'react';

export default function LabReportUpload({ patientId, onReportUploaded }) {
  const [file, setFile] = useState(null);
  const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('patient_id', patientId);
      formData.append('report_date', reportDate);
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/reports/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to upload report');
      }

      const result = await response.json();
      onReportUploaded(result);
      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="card-title">📄 Upload Lab Report</h2>

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

      <div className="form-group">
        <label className="form-label">Report Date</label>
        <input
          type="date"
          className="form-input"
          value={reportDate}
          onChange={(e) => setReportDate(e.target.value)}
        />
      </div>

      <div
        className={`file-upload ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileChange}
        />
        <div className="file-upload-icon">📋</div>
        {file ? (
          <div>
            <p style={{ color: 'var(--accent-green)', fontWeight: 600 }}>
              ✓ {file.name}
            </p>
            <p className="file-upload-text">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <div>
            <p className="file-upload-text">
              Drag & drop your lab report here
            </p>
            <p className="file-upload-text" style={{ fontSize: '0.85rem' }}>
              or click to browse (PDF, PNG, JPG)
            </p>
          </div>
        )}
      </div>

      <button
        className="btn btn-primary"
        onClick={handleUpload}
        disabled={loading || !file}
        style={{ marginTop: '1rem' }}
      >
        {loading ? (
          <>
            <span className="spinner" style={{ width: 20, height: 20 }}></span>
            Analyzing...
          </>
        ) : (
          <>🔬 Upload & Analyze</>
        )}
      </button>

      {loading && (
        <div style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>
          <p>🦙 Ollama is extracting data from your lab report...</p>
          <p style={{ fontSize: '0.85rem' }}>This may take a minute.</p>
        </div>
      )}
    </div>
  );
}
