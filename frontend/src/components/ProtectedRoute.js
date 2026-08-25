"use client";

import { useAuth } from '@/contexts/AuthContext';
import { redirect } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useEffect } from 'react';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      redirect('/login');
    }
  }, [loading, isAuthenticated]);

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-midnight/60 backdrop-blur-xl border border-white/5">
        <Loader2 className="w-12 h-12 text-cyber-cyan animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return children;
}
