'use client';

import { createContext, useContext, useEffect, useState } from 'react';

import { apiRequest } from '../lib/api';
import { AuthLoginResponse, User } from '../lib/lab-resources';

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

type AuthContextValue = {
  status: AuthStatus;
  user: User | null;
  login: (username: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [user, setUser] = useState<User | null>(null);

  async function refreshAuth() {
    try {
      const nextUser = await apiRequest<User>('/api/v1/auth/me');
      setUser(nextUser);
      setStatus('authenticated');
    } catch {
      setUser(null);
      setStatus('unauthenticated');
    }
  }

  async function login(username: string, password: string) {
    const response = await apiRequest<AuthLoginResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    setUser(response.user);
    setStatus('authenticated');
    return response.user;
  }

  async function logout() {
    try {
      await apiRequest<{ status: string }>('/api/v1/auth/logout', { method: 'POST' });
    } catch {
      // UI state should still clear even if the cookie was already missing.
    }
    setUser(null);
    setStatus('unauthenticated');
  }

  useEffect(() => {
    void refreshAuth();
  }, []);

  useEffect(() => {
    function handleAuthRequired() {
      setUser(null);
      setStatus('unauthenticated');
    }

    window.addEventListener('labos-auth-required', handleAuthRequired);
    return () => window.removeEventListener('labos-auth-required', handleAuthRequired);
  }, []);

  return (
    <AuthContext.Provider value={{ status, user, login, logout, refreshAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return context;
}
