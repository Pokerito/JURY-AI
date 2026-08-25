"use client";

import { useAuth } from '@/contexts/AuthContext';
import { LogOut, Scale, Menu } from 'lucide-react';
import Link from 'next/link';

export default function Navbar() {
  const { user, logout } = useAuth();

  const getRoleBadgeColor = (role) => {
    switch (role?.toLowerCase()) {
      case 'admin':
        return 'bg-cyber-cyan/20 text-cyber-cyan border-cyber-cyan/30';
      case 'analyst':
        return 'bg-cyber-green/20 text-cyber-green border-cyber-green/30';
      case 'viewer':
      default:
        return 'bg-cyber-yellow/20 text-cyber-yellow border-cyber-yellow/30';
    }
  };

  return (
    <nav className="sticky top-0 z-40 w-full bg-midnight/60 backdrop-blur-xl border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <Scale className="h-6 w-6 text-cyber-cyan" />
              <span className="text-xl font-bold text-white tracking-widest hidden sm:block">JURY-AI</span>
            </Link>
          </div>
          
          {user && (
            <div className="flex items-center space-x-4">
              <div className="hidden sm:flex items-center space-x-3">
                <span className="text-sm font-medium text-gray-200">{user.full_name}</span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${getRoleBadgeColor(user.role)}`}>
                  {user.role || 'user'}
                </span>
              </div>
              <button
                onClick={logout}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors flex items-center"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
