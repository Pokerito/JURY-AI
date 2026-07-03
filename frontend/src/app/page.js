"use client"
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  UploadCloud, ShieldAlert, ChevronRight, Activity, MessageSquare,
  FileText, X, BarChart2, Download, ExternalLink,
  Users, Calendar, DollarSign, Scale, History, CheckCircle
} from 'lucide-react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import toast, { Toaster } from 'react-hot-toast'
import { useRouter } from 'next/navigation'

// ── Skeleton ──────────────────────────────────────────────────────────────────
function Skeleton({ className = "" }) {
  return <div className={`animate-pulse rounded-lg bg-white/10 ${className}`} />
}

// ── Stat Badge ────────────────────────────────────────────────────────────────
function StatBadge({ count, label, colorClass }) {
  return (
    <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-mono ${colorClass}`}>
      <span className="font-bold text-sm">{count}</span>
      <span className="opacity-80">{label}</span>
    </div>
  )
}

// ── Time Ago helper ───────────────────────────────────────────────────────────
function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'Just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

// ─────────────────────────────────────────────────────────────────────────────
export default function CyberLegalDashboard() {
  const router = useRouter()

  // ── State ──────────────────────────────────────────────────────────────────
  const [file, setFile] = useState(null)
  const [fileUrl, setFileUrl] = useState(null)
  const [docId, setDocId] = useState(null)
  const [isUploading, setIsUploading] = useState(false)

  const [summary, setSummary] = useState(null)
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [showSummary, setShowSummary] = useState(true)

  const [entities, setEntities] = useState(null)           // Feature 10
  const [loadingEntities, setLoadingEntities] = useState(false)

  const [safetyData, setSafetyData] = useState(null)
  const [scoring, setScoring] = useState(false)

  const [query, setQuery] = useState("")
  const [messages, setMessages] = useState([])
  const [loadingMsg, setLoadingMsg] = useState(false)

  const [history, setHistory] = useState([])               // Feature 8
  const [showHistory, setShowHistory] = useState(false)
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false) // Feature 7

  // Feature 8 — load history from localStorage on mount
  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem('jury_ai_history') || '[]')
      setHistory(stored)
    } catch { setHistory([]) }
  }, [])

  // ── Upload ─────────────────────────────────────────────────────────────────
  const handleFileUpload = async (uploadedFile) => {
    if (!uploadedFile) return
    setFile(uploadedFile)
    setFileUrl(URL.createObjectURL(uploadedFile))
    setSummary(null); setSafetyData(null); setEntities(null)
    setMessages([]); setShowSummary(true)
    setIsUploading(true)
    const t = toast.loading('📄 Uploading & encoding vectors...')
    const fd = new FormData()
    fd.append("file", uploadedFile)
    try {
      const res = await fetch("http://localhost:8000/api/upload", { method: "POST", body: fd })
      const data = await res.json()
      if (res.ok) {
        setDocId(data.doc_id)
        toast.success('✅ Document uploaded!', { id: t })
        fetchSummary(data.doc_id)
        fetchEntities(data.doc_id)   // Feature 10 — auto fetch
      } else {
        toast.error(`❌ ${data.detail}`, { id: t })
      }
    } catch { toast.error('❌ Network error', { id: t }) }
    finally { setIsUploading(false) }
  }

  const fetchSummary = async (id) => {
    setLoadingSummary(true)
    const fd = new FormData(); fd.append("doc_id", id)
    try {
      const res = await fetch("http://localhost:8000/api/summary", { method: "POST", body: fd })
      const data = await res.json()
      if (res.ok) { setSummary(data.summary); toast.success('📋 Summary ready!') }
    } catch { }
    finally { setLoadingSummary(false) }
  }

  // Feature 10 — Named Entity Extraction
  const fetchEntities = async (id) => {
    setLoadingEntities(true)
    const fd = new FormData(); fd.append("doc_id", id)
    try {
      const res = await fetch("http://localhost:8000/api/entities", { method: "POST", body: fd })
      const data = await res.json()
      if (res.ok) setEntities(data.entities)
    } catch { }
    finally { setLoadingEntities(false) }
  }

  // ── Score ──────────────────────────────────────────────────────────────────
  const handleScoreDocument = async () => {
    if (!docId) return
    setScoring(true); setSafetyData(null)
    const t = toast.loading('🔍 Scanning for legal risks...')
    const fd = new FormData(); fd.append("doc_id", docId)
    try {
      const res = await fetch("http://localhost:8000/api/score", { method: "POST", body: fd })
      const data = await res.json()
      if (res.ok) {
        setSafetyData(data)
        saveToHistory(data)   // Feature 8
        const s = data.score
        if (s >= 80) toast.success(`✅ Score: ${s}/100 — Low Risk`, { id: t })
        else if (s >= 50) toast(`⚠️ Score: ${s}/100 — Medium Risk`, { id: t, icon: '⚠️' })
        else toast.error(`🚨 Score: ${s}/100 — High Risk!`, { id: t })
      } else { toast.error('❌ Analysis failed', { id: t }) }
    } catch { toast.error('❌ Network error', { id: t }) }
    finally { setScoring(false) }
  }

  // Feature 8 — save to localStorage
  const saveToHistory = (scoreData) => {
    const item = {
      doc_id: docId, filename: file?.name || 'Unknown',
      date: new Date().toISOString(), score: scoreData.score,
      summary, entities, checklist: scoreData.checklist, all_clauses: scoreData.all_clauses,
    }
    setHistory(prev => {
      const next = [item, ...prev.filter(h => h.doc_id !== docId)].slice(0, 10)
      localStorage.setItem('jury_ai_history', JSON.stringify(next))
      return next
    })
  }

  // Feature 8 — restore from history
  const loadFromHistory = (item) => {
    setDocId(item.doc_id)
    setFile({ name: item.filename })
    setFileUrl(null)
    setSummary(item.summary)
    setEntities(item.entities)
    setSafetyData({ score: item.score, checklist: item.checklist, all_clauses: item.all_clauses })
    setShowSummary(true); setShowHistory(false)
    toast.success(`📂 Loaded: ${item.filename}`)
  }

  // ── Chat ───────────────────────────────────────────────────────────────────
  const handleAsk = async () => {
    if (!query.trim()) return
    const newMsgs = [...messages, { role: "user", content: query }]
    setMessages(newMsgs); setQuery(""); setLoadingMsg(true)
    const fd = new FormData(); fd.append("query", query)
    try {
      const res = await fetch("http://localhost:8000/api/query", { method: "POST", body: fd })
      const data = await res.json()
      if (res.ok) setMessages([...newMsgs, { role: "assistant", content: data.answer }])
    } finally { setLoadingMsg(false) }
  }

  // Feature 7 — PDF Download
  const downloadPDF = async () => {
    if (!safetyData) return
    setIsGeneratingPDF(true)
    const t = toast.loading('📄 Generating PDF report...')
    try {
      const [{ default: jsPDF }, { default: autoTable }] = await Promise.all([
        import('jspdf'), import('jspdf-autotable')
      ])
      const doc = new jsPDF()
      const W = doc.internal.pageSize.getWidth()

      // Header banner
      doc.setFillColor(0, 70, 127)
      doc.rect(0, 0, W, 34, 'F')
      doc.setTextColor(255, 255, 255)
      doc.setFontSize(18); doc.setFont('helvetica', 'bold')
      doc.text('JURY-AI Legal Analysis Report', 14, 14)
      doc.setFontSize(9); doc.setFont('helvetica', 'normal')
      doc.text('AI-Powered Legal Risk Intelligence | DSATM, Bengaluru', 14, 23)
      doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30)

      // Score bar
      doc.setTextColor(30, 30, 30)
      doc.setFontSize(10); doc.setFont('helvetica', 'bold')
      doc.text(`File: ${file?.name || 'Unknown'}    Safety Score: ${safetyData.score} / 100`, 14, 44)
      const sc = safetyData.score
      const col = sc >= 80 ? [16, 185, 129] : sc >= 50 ? [251, 191, 36] : [244, 63, 94]
      doc.setFillColor(220, 220, 220); doc.rect(14, 48, 182, 6, 'F')
      doc.setFillColor(...col); doc.rect(14, 48, (sc / 100) * 182, 6, 'F')

      let y = 62

      // Summary
      if (summary) {
        doc.setFont('helvetica', 'bold'); doc.setFontSize(12); doc.text('Document Summary', 14, y); y += 6
        doc.setFont('helvetica', 'normal'); doc.setFontSize(9)
        const lines = doc.splitTextToSize(summary, 182)
        doc.text(lines, 14, y); y += lines.length * 5 + 8
      }

      // Entities table
      if (entities) {
        const rows = []
        if (entities.parties?.length) rows.push(['Parties', entities.parties.join(', ')])
        if (entities.dates?.length) rows.push(['Key Dates / Terms', entities.dates.join(', ')])
        if (entities.amounts?.length) rows.push(['Financial Amounts', entities.amounts.join(', ')])
        if (entities.jurisdictions?.length) rows.push(['Jurisdiction', entities.jurisdictions.join(', ')])
        if (rows.length) {
          autoTable(doc, {
            startY: y, head: [['Entity', 'Details']], body: rows,
            theme: 'grid',
            headStyles: { fillColor: [0, 70, 127], fontSize: 9 },
            styles: { fontSize: 9, cellPadding: 3 },
            columnStyles: { 0: { cellWidth: 48, fontStyle: 'bold' }, 1: { cellWidth: 134 } },
          })
          y = doc.lastAutoTable.finalY + 10
        }
      }

      // Risk clauses table — Feature 9 safer_alternative included
      if (safetyData.checklist?.length) {
        autoTable(doc, {
          startY: y,
          head: [['Clause', 'Risk', 'Justification', 'Safer Alternative']],
          body: safetyData.checklist.map(c => [c.clause_name, c.risk_level, c.justification, c.safer_alternative || '—']),
          theme: 'striped',
          headStyles: { fillColor: [0, 70, 127], fontSize: 9 },
          styles: { fontSize: 8, cellPadding: 2.5, overflow: 'linebreak' },
          columnStyles: { 0: { cellWidth: 40 }, 1: { cellWidth: 18 }, 2: { cellWidth: 62 }, 3: { cellWidth: 62 } },
        })
      }

      // Page footer
      const pages = doc.internal.getNumberOfPages()
      for (let i = 1; i <= pages; i++) {
        doc.setPage(i)
        doc.setFontSize(8); doc.setTextColor(150)
        doc.text('JURY-AI | Dayananda Sagar Academy of Technology and Management', 14, doc.internal.pageSize.getHeight() - 8)
        doc.text(`Page ${i} of ${pages}`, W - 28, doc.internal.pageSize.getHeight() - 8)
      }

      doc.save(`JURY-AI-${(file?.name || 'report').replace(/\.[^/.]+$/, '')}.pdf`)
      toast.success('📄 PDF downloaded!', { id: t })
    } catch (e) {
      console.error(e); toast.error('❌ Failed to generate PDF', { id: t })
    } finally { setIsGeneratingPDF(false) }
  }

  // Feature 11 — Navigate to full report page
  const navigateToReport = () => {
    if (!safetyData || !docId) return
    const reportData = {
      doc_id: docId, filename: file?.name, score: safetyData.score,
      checklist: safetyData.checklist, all_clauses: safetyData.all_clauses,
      summary, entities, messages, date: new Date().toISOString(),
    }
    localStorage.setItem(`jury_report_${docId}`, JSON.stringify(reportData))
    router.push(`/report/${docId}`)
  }

  // ── Gauge math ─────────────────────────────────────────────────────────────
  const radius = 50, circumference = 2 * Math.PI * radius
  const scoreValue = safetyData?.score ?? 0
  const strokeDashoffset = circumference - (scoreValue / 100) * circumference
  const gaugeColor = scoreValue >= 80 ? '#10B981' : scoreValue >= 50 ? '#FBBF24' : '#F43F5E'

  // Clause counts for stats bar + pie chart
  const allClauses = safetyData?.all_clauses || []
  const countOf = (l) => allClauses.filter(c => c.risk_level?.toLowerCase() === l.toLowerCase()).length
  const [nCrit, nHigh, nMed, nLow] = ['critical', 'high', 'medium', 'low'].map(countOf)
  const pieData = [
    { name: 'Critical', value: nCrit, color: '#F43F5E' },
    { name: 'High', value: nHigh, color: '#FBBF24' },
    { name: 'Medium', value: nMed, color: '#60A5FA' },
    { name: 'Low / Safe', value: Math.max(nLow, nCrit + nHigh + nMed === 0 && safetyData ? 1 : 0), color: '#10B981' },
  ].filter(d => d.value > 0)

  // Entity display config
  const entitySections = [
    { key: 'parties', label: 'Parties', Icon: Users, color: 'text-cyber-cyan' },
    { key: 'dates', label: 'Key Dates', Icon: Calendar, color: 'text-purple-400' },
    { key: 'amounts', label: 'Amounts', Icon: DollarSign, color: 'text-green-400' },
    { key: 'jurisdictions', label: 'Jurisdiction', Icon: Scale, color: 'text-orange-400' },
  ]

  // ─────────────────────────────────────────────────────────────────────────
  return (
    <div className="flex h-screen w-full bg-midnight-dark p-4 gap-4 overflow-hidden font-sans">

      <Toaster position="top-right" toastOptions={{
        duration: 4000,
        style: { background: '#1E293B', color: '#e2e8f0', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '13px' }
      }} />

      {/* ═══ LEFT PANEL ════════════════════════════════════════════════════════ */}
      <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
        className="w-1/2 h-full glass-panel rounded-2xl flex flex-col p-6 overflow-hidden relative">

        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center border border-cyan-500/50 shadow-glow-cyan">
              <ShieldAlert className="text-cyber-cyan w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-wide">Jury-AI</h1>
              <p className="text-xs text-slate-400 font-mono">System.Context.Viewer</p>
            </div>
          </div>

          {/* Feature 8 — History button */}
          <button onClick={() => setShowHistory(v => !v)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-mono transition-all ${showHistory ? 'bg-cyber-cyan/20 border-cyber-cyan/50 text-cyber-cyan' : 'border-white/10 text-slate-400 hover:border-white/20 hover:text-white'}`}>
            <History className="w-3.5 h-3.5" /> History
            {history.length > 0 && <span className="bg-cyber-cyan text-midnight-dark px-1.5 py-0.5 rounded-full text-[10px] font-bold">{history.length}</span>}
          </button>
        </div>

        {/* Feature 8 — History drawer overlay */}
        <AnimatePresence>
          {showHistory && (
            <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
              className="absolute top-20 left-6 right-6 z-30 glass-panel rounded-xl border border-white/10 shadow-2xl overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-white/5">
                <span className="text-sm font-semibold text-white flex items-center gap-2">
                  <History className="w-4 h-4 text-cyber-cyan" /> Recent Analyses
                </span>
                <button onClick={() => setShowHistory(false)} className="text-slate-500 hover:text-white transition-colors"><X className="w-4 h-4" /></button>
              </div>
              <div className="max-h-60 overflow-y-auto">
                {history.length === 0 ? (
                  <p className="text-slate-500 text-sm text-center py-8">No history yet — analyse a document first</p>
                ) : history.map((item, i) => (
                  <button key={i} onClick={() => loadFromHistory(item)}
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors border-b border-white/5 last:border-0 text-left">
                    <FileText className="w-4 h-4 text-slate-500 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white truncate">{item.filename}</p>
                      <p className="text-[11px] text-slate-500">{timeAgo(item.date)}</p>
                    </div>
                    <span className={`text-xs font-bold px-2 py-1 rounded-lg ${item.score >= 80 ? 'bg-green-500/20 text-green-400' : item.score >= 50 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}`}>
                      {item.score}/100
                    </span>
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Document Viewer */}
        {!fileUrl ? (
          <div className="flex-1 border-2 border-dashed border-white/10 rounded-xl hover:border-cyber-cyan/50 hover:bg-cyber-cyan/5 transition-all flex flex-col items-center justify-center cursor-pointer relative group">
            <input type="file" accept=".pdf,.txt,.docx" className="absolute inset-0 opacity-0 cursor-pointer"
              onChange={(e) => handleFileUpload(e.target.files[0])} />
            <UploadCloud className="w-12 h-12 text-slate-500 group-hover:text-cyber-cyan transition-colors mb-4" />
            <p className="text-slate-300 font-medium">Inject Legal Document Base</p>
            <p className="text-sm text-slate-500 mt-2">.pdf, .docx, .txt supported</p>
          </div>
        ) : (
          <div className="flex-1 bg-white/5 rounded-xl overflow-hidden border border-white/10 flex flex-col">
            <div className="bg-white/5 py-2 px-4 text-sm font-mono text-cyan-400 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" /> TARGET: {file?.name}
            </div>
            {isUploading ? (
              <div className="flex-1 flex flex-col items-center justify-center text-cyber-cyan">
                <Activity className="animate-spin w-8 h-8 mb-4" />
                <div className="w-48 space-y-2 mt-2"><Skeleton className="h-3 w-full" /><Skeleton className="h-3 w-4/5" /><Skeleton className="h-3 w-3/5" /></div>
                <p className="font-mono text-sm animate-pulse mt-4">Encoding Vectors...</p>
              </div>
            ) : file?.name?.endsWith?.('.pdf') ? (
              <object data={fileUrl} type="application/pdf" className="w-full h-full" />
            ) : (
              <iframe src={fileUrl} className="w-full h-full bg-white text-black p-4" />
            )}
          </div>
        )}
      </motion.div>

      {/* ═══ RIGHT PANEL ═══════════════════════════════════════════════════════ */}
      <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
        className="w-1/2 h-full flex flex-col gap-3 overflow-y-auto">

        {/* Feature 7 + 11 — Action Bar (shown after scoring) */}
        <AnimatePresence>
          {safetyData && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex gap-2 flex-shrink-0">
              <button onClick={downloadPDF} disabled={isGeneratingPDF}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-cyber-cyan/10 hover:bg-cyber-cyan/20 border border-cyber-cyan/30 text-cyber-cyan text-sm font-mono transition-all disabled:opacity-50">
                {isGeneratingPDF ? <Activity className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                {isGeneratingPDF ? 'Generating...' : 'Download Report'}
              </button>
              <button onClick={navigateToReport}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-400 text-sm font-mono transition-all">
                <ExternalLink className="w-4 h-4" /> Full Report
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Gauge Card */}
        <div className="glass-panel rounded-2xl p-5 flex flex-col gap-3 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex-1 pr-4">
              <h2 className="text-xl font-bold text-white mb-1">Quantitative Safety</h2>
              <p className="text-xs text-slate-400 mb-4 leading-relaxed">Algorithmically derives legal risk by indexing High and Critical liabilities.</p>
              <button onClick={handleScoreDocument} disabled={scoring || !docId}
                className="w-max bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 py-2 px-5 rounded-lg font-mono text-sm transition-all disabled:opacity-50 flex items-center gap-2">
                <Activity className={`w-4 h-4 ${scoring ? 'animate-spin' : ''}`} />
                {scoring ? 'EXECUTING SCAN...' : 'INITIATE ANALYSIS'}
              </button>
            </div>
            <div className="relative w-36 h-36 flex-shrink-0">
              <svg className="-rotate-90 w-full h-full" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r={radius} stroke="rgba(255,255,255,0.1)" strokeWidth="8" fill="none" />
                <motion.circle cx="60" cy="60" r={radius} stroke={gaugeColor} strokeWidth="8" fill="none" strokeLinecap="round"
                  initial={{ strokeDasharray: circumference, strokeDashoffset: circumference }}
                  animate={{ strokeDashoffset: safetyData ? strokeDashoffset : circumference }}
                  transition={{ duration: 1.5, ease: "easeOut" }} />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-bold text-white">{scoreValue}</span>
                <span className="text-[10px] text-slate-400 font-mono">/ 100 IDX</span>
              </div>
            </div>
          </div>

          {/* Stat badges */}
          <AnimatePresence>
            {safetyData && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="flex flex-wrap gap-2 pt-3 border-t border-white/10">
                {nCrit > 0 && <StatBadge count={nCrit} label="Critical" colorClass="bg-red-500/10 border-red-500/30 text-red-400" />}
                {nHigh > 0 && <StatBadge count={nHigh} label="High" colorClass="bg-yellow-500/10 border-yellow-500/30 text-yellow-400" />}
                {nMed > 0 && <StatBadge count={nMed} label="Medium" colorClass="bg-blue-500/10 border-blue-500/30 text-blue-400" />}
                {nLow > 0 && <StatBadge count={nLow} label="Low" colorClass="bg-green-500/10 border-green-500/30 text-green-400" />}
                {nCrit === 0 && nHigh === 0 && <StatBadge count="✓" label="All Clear" colorClass="bg-green-500/10 border-green-500/30 text-green-400" />}
              </motion.div>
            )}
            {scoring && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-2 pt-3 border-t border-white/10">
                <Skeleton className="h-7 w-24" /><Skeleton className="h-7 w-20" /><Skeleton className="h-7 w-16" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Feature 10 — Named Entities Card */}
        <AnimatePresence>
          {(loadingEntities || entities) && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-panel rounded-2xl p-4 flex-shrink-0">
              <div className="flex items-center gap-2 mb-3">
                <Users className="w-4 h-4 text-cyber-cyan" />
                <h3 className="text-sm font-semibold text-white">Named Entities</h3>
                {loadingEntities && <span className="text-[10px] font-mono text-slate-500 animate-pulse">Extracting...</span>}
              </div>
              {loadingEntities ? (
                <div className="grid grid-cols-2 gap-2">{[...Array(4)].map((_, i) => <Skeleton key={i} className="h-14" />)}</div>
              ) : (
                <div className="grid grid-cols-2 gap-2">
                  {entitySections.map(({ key, label, Icon, color }) => {
                    const items = entities?.[key] || []
                    if (!items.length) return null
                    return (
                      <div key={key} className="glass-card p-3 rounded-xl">
                        <div className={`flex items-center gap-1.5 mb-2 ${color}`}>
                          <Icon className="w-3.5 h-3.5" />
                          <span className="text-[11px] font-semibold uppercase tracking-wide">{label}</span>
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {items.slice(0, 3).map((item, i) => (
                            <span key={i} className="text-[10px] bg-white/5 border border-white/10 rounded-md px-2 py-0.5 text-slate-300 truncate max-w-full">{item}</span>
                          ))}
                          {items.length > 3 && <span className="text-[10px] text-slate-500">+{items.length - 3} more</span>}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Summary Card */}
        <AnimatePresence>
          {(loadingSummary || summary) && showSummary && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="glass-panel rounded-2xl p-4 flex-shrink-0">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-cyber-cyan" />
                  <h3 className="text-sm font-semibold text-white">Document Summary</h3>
                  {loadingSummary && <span className="text-[10px] font-mono text-slate-500 animate-pulse">Generating...</span>}
                </div>
                <button onClick={() => setShowSummary(false)} className="text-slate-500 hover:text-white transition-colors p-1"><X className="w-4 h-4" /></button>
              </div>
              {loadingSummary ? (
                <div className="space-y-2"><Skeleton className="h-3 w-full" /><Skeleton className="h-3 w-5/6" /><Skeleton className="h-3 w-4/6" /></div>
              ) : (
                <p className="text-sm text-slate-300 leading-relaxed">{summary}</p>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Pie Chart */}
        <AnimatePresence>
          {safetyData && pieData.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-panel rounded-2xl p-4 flex-shrink-0">
              <div className="flex items-center gap-2 mb-3">
                <BarChart2 className="w-4 h-4 text-cyber-cyan" />
                <h3 className="text-sm font-semibold text-white">Risk Distribution</h3>
              </div>
              <div className="flex items-center gap-4">
                <ResponsiveContainer width="50%" height={120}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={35} outerRadius={52} paddingAngle={3} dataKey="value">
                      {pieData.map((e, i) => <Cell key={i} fill={e.color} />)}
                    </Pie>
                    <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '12px', color: '#e2e8f0' }} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex flex-col gap-1.5">
                  {pieData.map((e, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: e.color }} />
                      <span className="text-slate-300">{e.name}</span>
                      <span className="font-bold text-white ml-auto pl-2">{e.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Operations Feed */}
        <div className="flex-1 glass-panel rounded-2xl overflow-hidden flex flex-col min-h-[280px]">
          <div className="flex items-center border-b border-white/10 px-6 py-3 bg-white/5">
            <div className="text-sm font-medium text-white flex items-center gap-2">
              <MessageSquare className="w-4 h-4" /> Operations Feed
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
            <AnimatePresence>
              {/* Feature 9 — Risk cards WITH safer_alternative */}
              {safetyData?.checklist?.map((item, idx) => (
                <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.08 }}
                  className={`glass-card p-4 rounded-xl border-l-4 ${item.risk_level === 'Critical' ? 'border-l-cyber-red' : 'border-l-cyber-yellow'}`}>
                  <h4 className="text-white font-semibold flex items-center gap-2 text-sm">
                    <ShieldAlert className={`w-4 h-4 flex-shrink-0 ${item.risk_level === 'Critical' ? 'text-cyber-red' : 'text-cyber-yellow'}`} />
                    {item.clause_name}
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/10 ml-auto font-mono">{item.risk_level}</span>
                  </h4>
                  <p className="mt-2 text-sm text-slate-300 leading-relaxed">{item.justification}</p>
                  {item.safer_alternative && (
                    <div className="mt-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <CheckCircle className="w-3.5 h-3.5 text-green-400" />
                        <span className="text-[11px] font-semibold text-green-400 uppercase tracking-wide">Suggested Alternative</span>
                      </div>
                      <p className="text-xs text-green-200 leading-relaxed">{item.safer_alternative}</p>
                    </div>
                  )}
                </motion.div>
              ))}

              {/* Chat messages */}
              {messages.map((m, i) => (
                <div key={i} className={`flex flex-col gap-1 max-w-[90%] ${m.role === 'user' ? 'self-end items-end' : 'self-start items-start'}`}>
                  <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider px-1">
                    {m.role === 'user' ? 'Client Request' : 'Standard RAG Generation'}
                  </div>
                  <div className={`p-4 rounded-xl text-sm leading-relaxed whitespace-pre-wrap ${m.role === 'user' ? 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-50' : 'bg-white/5 border border-white/10 text-slate-200'}`}>
                    {m.content}
                  </div>
                </div>
              ))}

              {loadingMsg && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="self-start flex flex-col gap-2 max-w-[80%]">
                  <div className="text-[10px] font-mono text-slate-500 uppercase">Legal Agent Thinking...</div>
                  <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2 w-56">
                    <Skeleton className="h-3 w-full" /><Skeleton className="h-3 w-5/6" /><Skeleton className="h-3 w-3/5" />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="p-4 border-t border-white/10 bg-white/5">
            <div className="relative flex items-center">
              <input className="w-full bg-midnight-dark border border-white/20 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan transition-all placeholder:text-slate-500"
                placeholder="Instruct Orchestrator Agents..."
                value={query} onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleAsk()} />
              <button className="absolute right-2 p-2 bg-cyber-cyan/20 hover:bg-cyber-cyan/40 text-cyber-cyan rounded-lg transition-colors" onClick={handleAsk}>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

      </motion.div>
    </div>
  )
}
