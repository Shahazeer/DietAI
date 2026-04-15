import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

// Only persist the bare minimum needed to render the UI — no PII/health data.
// Full profile is fetched from /api/auth/me on mount to verify the token is valid.
function _storeMinimalUser(user) {
  localStorage.setItem('user_meta', JSON.stringify({ id: user.id, name: user.name }));
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [authReady, setAuthReady] = useState(false);

  // MED-5: On mount, verify the stored token against the server before trusting it.
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setAuthReady(true);
      return;
    }
    api.get('/api/auth/me')
      .then(({ data }) => {
        setUser(data);
        _storeMinimalUser(data);
      })
      .catch(() => {
        // Token invalid or expired — clear everything
        localStorage.removeItem('token');
        localStorage.removeItem('user_meta');
        setUser(null);
      })
      .finally(() => setAuthReady(true));
  }, []);

  const login = useCallback(async (email, password) => {
    const { data } = await api.post('/api/auth/login', { email, password });
    localStorage.setItem('token', data.access_token);
    _storeMinimalUser(data.user);
    setUser(data.user);
    return data.user;
  }, []);

  const register = useCallback(async (formData) => {
    const { data } = await api.post('/api/auth/register', formData);
    localStorage.setItem('token', data.access_token);
    _storeMinimalUser(data.user);
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_meta');
    setUser(null);
  }, []);

  // Don't render children until the token verification resolves — prevents
  // a flash of authenticated content before the /me check completes.
  if (!authReady) return null;

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
