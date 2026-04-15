import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const PIPELINE_STEPS = [
  {
    num: '01',
    title: 'Vision Extraction',
    desc: 'Qwen2.5-VL reads every page and transcribes lab values',
    color: 'step-green',
  },
  {
    num: '02',
    title: 'AI Contemplation',
    desc: 'Llama 3.1 validates, deduplicates, and structures the data',
    color: 'step-blue',
  },
  {
    num: '03',
    title: 'Diet Generation',
    desc: 'RAG-powered 7-day meal plan tailored to your biomarkers',
    color: 'step-purple',
  },
];

export default function NewReportPage() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState('');
  const [error, setError] = useState('');
  const fileRef = useRef();
  const navigate = useNavigate();

  const STAGES = [
    { key: 'upload', label: 'Uploading file…' },
    { key: 'vision', label: 'Vision model reading report…' },
    { key: 'contemplate', label: 'Contemplating extracted data…' },
    { key: 'done', label: 'Complete!' },
  ];

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped?.type === 'application/pdf') {
      setFile(dropped);
      setError('');
    } else {
      setError('Only PDF files are accepted.');
    }
  };

  const handleFileChange = (e) => {
    const chosen = e.target.files[0];
    if (chosen?.type === 'application/pdf') {
      setFile(chosen);
      setError('');
    } else {
      setError('Only PDF files are accepted.');
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
      await api.post('/api/reports/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setStage('done');
      setTimeout(() => navigate('/dashboard'), 800);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      setLoading(false);
      setStage('');
    }
  };

  const currentStageIdx = STAGES.findIndex((s) => s.key === stage);

  return (
    <div className="page-wrap">
      <header className="page-header">
        <h1>Upload Lab Report</h1>
        <p className="page-header-sub">
          Our 3-stage AI pipeline extracts every biomarker and generates a personalised 7-day nutrition plan.
        </p>
      </header>

      <div className="upload-layout">
        {/* Upload card */}
        <div className="upload-card">
          <form onSubmit={handleSubmit}>
            <div
              className={`drop-zone${dragging ? ' dragging' : ''}${file ? ' has-file' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onClick={() => !loading && fileRef.current?.click()}
              role="button"
              tabIndex={0}
              aria-label="Click or drag to upload a PDF"
              onKeyDown={(e) => e.key === 'Enter' && !loading && fileRef.current?.click()}
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
                  <div className="drop-file-icon">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                  </div>
                  <div className="drop-file-info">
                    <span className="drop-filename">{file.name}</span>
                    <span className="drop-filesize">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                  {!loading && (
                    <button
                      type="button"
                      className="drop-remove"
                      onClick={(e) => { e.stopPropagation(); setFile(null); }}
                      aria-label="Remove file"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ) : (
                <div className="drop-placeholder">
                  <div className="drop-upload-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="17 8 12 3 7 8" />
                      <line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                  </div>
                  <p className="drop-title">Drag & drop your PDF here</p>
                  <p className="drop-hint">or click to browse · Max 20 MB</p>
                </div>
              )}
            </div>

            {error && (
              <div className="auth-error" role="alert" style={{ marginTop: '1rem' }}>
                {error}
              </div>
            )}

            {loading && (
              <div className="upload-progress">
                <div className="progress-track">
                  {STAGES.filter((s) => s.key !== 'done').map((s, i) => (
                    <div
                      key={s.key}
                      className={`progress-step${i < currentStageIdx ? ' done' : i === currentStageIdx ? ' active' : ''}`}
                    >
                      <div className="progress-step-dot">
                        {i < currentStageIdx ? (
                          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                        ) : null}
                      </div>
                      <span className="progress-step-label">{s.label}</span>
                    </div>
                  ))}
                </div>
                <div className="upload-spinner-row">
                  <div className="spinner" />
                  <p className="upload-hint">
                    {stage === 'vision' || stage === 'contemplate'
                      ? 'This can take 2–5 minutes depending on report length…'
                      : 'Processing…'}
                  </p>
                </div>
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
        </div>

        {/* Pipeline steps */}
        <div className="pipeline-card">
          <h3 className="pipeline-title">How it works</h3>
          <div className="pipeline-steps">
            {PIPELINE_STEPS.map((step) => (
              <div key={step.num} className={`pipeline-step ${step.color}`}>
                <div className="step-num">{step.num}</div>
                <div className="step-body">
                  <strong className="step-title">{step.title}</strong>
                  <p className="step-desc">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="pipeline-note">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>Duplicate uploads are automatically detected and rejected.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
