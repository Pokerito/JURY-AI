"use client";

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Scale, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import toast, { Toaster } from 'react-hot-toast';
import Link from 'next/link';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    full_name: '',
    org_name: '',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    setLoading(true);
    try {
      await register(formData);
    } catch (error) {
      toast.error(error.message || 'Failed to register account');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-midnight p-4">
      <Toaster position="top-right" />
      <motion.div 
        initial={{ opacity: 0, y: 20 }} 
        animate={{ opacity: 1, y: 0 }} 
        transition={{ duration: 0.5 }}
        className="w-full max-w-md bg-midnight/60 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-2xl"
      >
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-cyber-cyan/10 rounded-full mb-4 border border-cyber-cyan/20">
            <Scale className="w-8 h-8 text-cyber-cyan" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-wider">JURY-AI</h1>
          <p className="text-gray-400 mt-2 text-sm">Create a new account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Full Name</label>
            <input 
              type="text" 
              name="full_name"
              required 
              value={formData.full_name}
              onChange={handleChange}
              className="w-full bg-midnight-light border border-white/10 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan transition-colors"
              placeholder="John Doe"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Organization Name</label>
            <input 
              type="text" 
              name="org_name"
              required 
              value={formData.org_name}
              onChange={handleChange}
              className="w-full bg-midnight-light border border-white/10 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan transition-colors"
              placeholder="Acme Corp"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Email</label>
            <input 
              type="email" 
              name="email"
              required 
              value={formData.email}
              onChange={handleChange}
              className="w-full bg-midnight-light border border-white/10 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan transition-colors"
              placeholder="name@company.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Password</label>
            <input 
              type="password" 
              name="password"
              required 
              minLength={8}
              value={formData.password}
              onChange={handleChange}
              className="w-full bg-midnight-light border border-white/10 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan transition-colors"
              placeholder="••••••••"
            />
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full py-3 px-4 flex items-center justify-center rounded-lg bg-gradient-to-r from-cyan-500 to-cyan-400 text-midnight-dark font-semibold hover:shadow-[0_0_15px_rgba(34,211,238,0.5)] transition-all disabled:opacity-70 disabled:cursor-not-allowed mt-4"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-400">
          Already have an account?{' '}
          <Link href="/login" className="text-cyber-cyan hover:underline hover:text-cyan-400 transition-colors">
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
