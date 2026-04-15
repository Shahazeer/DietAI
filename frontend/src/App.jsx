import { Component } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import NewReportPage from './pages/NewReportPage';
import './index.css';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-boundary-icon">⚠</div>
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message ?? 'An unexpected error occurred.'}</p>
          <button
            className="btn btn-primary"
            onClick={() => this.setState({ hasError: false, error: null })}
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function AppLayout() {
  const location = useLocation();
  const { user } = useAuth();

  const authPaths = ['/login', '/register'];
  const isAuthPage = authPaths.includes(location.pathname);
  // AuthProvider already returns null until auth is resolved, so by the time
  // AppLayout renders, the token check is always complete. No need for authReady.
  const showSidebar = !isAuthPage && !!user;

  return (
    <div className={`app-shell${showSidebar ? ' with-sidebar' : ''}`}>
      {showSidebar && <Sidebar />}
      <main className="app-main">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/new-report"
            element={
              <ProtectedRoute>
                <NewReportPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ErrorBoundary>
          <AppLayout />
        </ErrorBoundary>
      </AuthProvider>
    </BrowserRouter>
  );
}
