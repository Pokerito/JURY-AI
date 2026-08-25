"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';

const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchUser = async () => {
      const token = api.getToken();
      if (token) {
        try {
          const userData = await api.getMe();
          setUser(userData);
        } catch (error) {
          console.error('Failed to fetch user', error);
          api.clearTokens();
        }
      }
      setLoading(false);
    };

    fetchUser();
  }, []);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    api.setTokens(data.access_token, data.refresh_token);
    const userData = await api.getMe();
    setUser(userData);
    router.push('/dashboard');
  };

  const register = async (userData) => {
    const data = await api.register(userData);
    api.setTokens(data.access_token, data.refresh_token);
    const newUserData = await api.getMe();
    setUser(newUserData);
    router.push('/dashboard');
  };

  const logout = () => {
    api.clearTokens();
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
