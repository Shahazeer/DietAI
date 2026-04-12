import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function NewReportPage() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState('');
  const [error, setError] = useState('');
  const fileRef = useRef();
  const navigate = useNavigate();

  const STAGES = [
    { key: 'upload', label: 'Uploading file...' },
    { key: 'vision', label: 'Vision model reading report...' },
    { key: 'contemplate', label: 'Contemplating extracted data...' },
    { key: 'done', label: 'Done!' },
  ];

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped?.type === 'application/pdf') setFile(dropped);
    else setError('Please upload a PDF file.');
  };

  const handleFileChange = (e) => {
    const chosen = e.target.files[0];
    if (chosen?.type === 'application/pdf') {
      setFile(chosen);
      setError('');
    } else {
      setError('Please upload a PDF file.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a PDF file.');
      return;
    }
    setError('');
    setLoading(true);
    setStage('upload');

    const formData = new FormData();
    formData.append('file', file);

    try {
      setStage('vision');
      const { data } = await api.post('/api/reports/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setStage('done');
      // Navigate to dashboard, which will show the new report
      setTimeout(() => navigate('/dashboard'), 800);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      setLoading(false);
      setStage('');
    }
  };

  const currentStageLabel = STAGES.find((s) => s.key === stage)?.label || '';

  return (
    <div className="new-report-page">
      <div className="new-report-card">
        <h2>Upload Lab Report</h2>
        <p className="page-sub">
          Upload a PDF of your blood work or lab report. Our 3-stage AI pipeline will extract all values and generate a personalized diet plan.
        </p>

        <form onSubmit={handleSubmit}>
          <div
            className={`drop-zone ${dragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
          >
            <input
              type="file"
              accept=".pdf"
              ref={fileRef}
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            {file ? (
              <div className="drop-selected">
                <span className="drop-icon">📄</span>
                <span className="drop-filename">{file.name}</span>
                <span className="drop-size">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
              </div>
            ) : (
              <div className="drop-placeholder">
                <span className="drop-icon">☁</span>
                <p>Drag & drop your PDF here</p>
                <p className="drop-hint">or click to browse</p>
              </div>
            )}
          </div>

          {error && <div className="auth-error" style={{ marginTop: '1rem' }}>{error}</div>}

          {loading && (
            <div className="upload-progress">
              <div className="spinner" />
              <div className="progress-stages">
                {STAGES.filter((s) => s.key !== 'done').map((s) => (
                  <div
                    key={s.key}
                    className={`progress-stage ${stage === s.key ? 'active' : ''}`}
                  >
                    {s.label}
                  </div>
                ))}
              </div>
              <p className="stage-hint">
                {stage === 'vision' || stage === 'contemplate'
                  ? 'This can take 2–5 minutes depending on report size.'
                  : ''}
              </p>
            </div>
          )}

          {!loading && (
            <button
              type="submit"
              className="btn btn-primary btn-full"
              style={{ marginTop: '1.5rem' }}
              disabled={!file}
            >
              Analyse Report
            </button>
          )}
        </form>

        <div className="pipeline-info">
          <h4>How it works</h4>
          <div className="pipeline-steps">
            <div className="pipeline-step">
              <span className="step-num">1</span>
              <div>
                <strong>Vision Extraction</strong>
                <p>Qwen2.5-VL reads every page and transcribes all values</p>
              </div>
            </div>
            <div className="pipeline-step">
              <span className="step-num">2</span>
              <div>
                <strong>AI Contemplation</strong>
                <p>Llama 3.1 validates, deduplicates, and structures the data</p>
              </div>
            </div>
            <div className="pipeline-step">
              <span className="step-num">3</span>
              <div>
                <strong>Diet Generation</strong>
                <p>A personalized 7-day meal plan using RAG knowledge base</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
