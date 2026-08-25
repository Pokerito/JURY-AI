"use client"
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { Scale, ArrowRight, Shield, Zap, FileSearch } from 'lucide-react'
import { motion } from 'framer-motion'

export default function HomePage() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.replace('/dashboard')
    }
  }, [loading, isAuthenticated, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Scale className="w-8 h-8 text-cyber-cyan animate-pulse" />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <div className="flex-1 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="text-center max-w-3xl mx-auto"
        >
          {/* Logo */}
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="inline-flex items-center gap-3 mb-8"
          >
            <div className="p-3 rounded-xl bg-cyber-cyan/10 border border-cyber-cyan/20">
              <Scale className="w-10 h-10 text-cyber-cyan" />
            </div>
            <h1 className="text-5xl font-bold tracking-tight">
              <span className="text-cyber-cyan">JURY</span>
              <span className="text-slate-200">-AI</span>
            </h1>
          </motion.div>

          <p className="text-xl text-slate-400 mb-4 leading-relaxed">
            AI-Powered Legal Document Intelligence Platform
          </p>
          <p className="text-slate-500 mb-10 max-w-xl mx-auto">
            Upload a legal contract. Get an instant risk analysis with safety scoring,
            clause detection, entity extraction, and AI-powered Q&A — all in seconds.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => router.push('/register')}
              className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-cyan-400 text-midnight-dark font-semibold rounded-xl px-8 py-4 text-lg hover:shadow-glow-cyan transition-shadow"
            >
              Get Started Free
              <ArrowRight className="w-5 h-5" />
            </motion.button>
            <button
              onClick={() => router.push('/login')}
              className="flex items-center gap-2 glass-card rounded-xl px-8 py-4 text-lg text-slate-300 hover:text-cyber-cyan transition-colors"
            >
              Sign In
            </button>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl mx-auto">
            {[
              { icon: Shield, label: 'Risk Scoring', desc: '0-100 safety score' },
              { icon: FileSearch, label: 'Clause Detection', desc: 'Critical to Low risk' },
              { icon: Zap, label: 'RAG Q&A', desc: 'Ask questions about any doc' },
            ].map((feat, i) => (
              <motion.div
                key={feat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + i * 0.15, duration: 0.5 }}
                className="glass-card rounded-xl p-5 text-center"
              >
                <feat.icon className="w-6 h-6 text-cyber-cyan mx-auto mb-3" />
                <p className="text-sm font-semibold text-slate-200">{feat.label}</p>
                <p className="text-xs text-slate-500 mt-1">{feat.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="text-center py-6 text-slate-600 text-sm">
        Built by Team JURY-AI · DSATM Bengaluru
      </footer>
    </div>
  )
}
