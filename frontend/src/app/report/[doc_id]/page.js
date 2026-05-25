"use client"
import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  ShieldAlert, ArrowLeft, Download, Users, Calendar,
  DollarSign, Scale, CheckCircle, FileText, BarChart2
} from 'lucide-react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'

export default function ReportPage() {
  const { doc_id } = useParams()
  const router = useRouter()
  const [data, setData] = useState(null)

  useEffect(() => {
    try {
      const stored = localStorage.getItem(`jury_report_${doc_id}`)
      if (stored) setData(JSON.parse(stored))
    } catch { }
  }, [doc_id])

  if (!data) {
    return (
      <div className="min-h-screen bg-midnight-dark flex items-center justify-center">
        <div className="text-center">
          <ShieldAlert className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 font-mono">No report data found.</p>
          <button onClick={() => router.push('/')} className="mt-4 text-cyber-cyan hover:underline text-sm">
            ← Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  const allClauses = data.all_clauses || []
  const countOf = (l) => allClauses.filter(c => c.risk_level?.toLowerCase() === l).length
  const [nCrit, nHigh, nMed, nLow] = ['critical', 'high', 'medium', 'low'].map(countOf)

  const pieData = [
    { name: 'Critical', value: nCrit, color: '#F43F5E' },
    { name: 'High', value: nHigh, color: '#FBBF24' },
    { name: 'Medium', value: nMed, color: '#60A5FA' },
    { name: 'Low / Safe', value: Math.max(nLow, 1), color: '#10B981' },
  ].filter(d => d.value > 0)

  const barData = [
    { name: 'Critical', count: nCrit, fill: '#F43F5E' },
    { name: 'High', count: nHigh, fill: '#FBBF24' },
    { name: 'Medium', count: nMed, fill: '#60A5FA' },
    { name: 'Low', count: nLow, fill: '#10B981' },
  ]

  const scoreColor = data.score >= 80 ? '#10B981' : data.score >= 50 ? '#FBBF24' : '#F43F5E'
  const scoreLabel = data.score >= 80 ? 'LOW RISK' : data.score >= 50 ? 'MEDIUM RISK' : 'HIGH RISK'

  const entitySections = [
    { key: 'parties', label: 'Parties', Icon: Users, color: 'text-cyber-cyan', bg: 'bg-cyan-500/10 border-cyan-500/20' },
    { key: 'dates', label: 'Key Dates', Icon: Calendar, color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20' },
    { key: 'amounts', label: 'Amounts', Icon: DollarSign, color: 'text-green-400', bg: 'bg-green-500/10 border-green-500/20' },
    { key: 'jurisdictions', label: 'Jurisdiction', Icon: Scale, color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20' },
  ]

  const downloadPDF = async () => {
    try {
      const [{ default: jsPDF }, { default: autoTable }] = await Promise.all([import('jspdf'), import('jspdf-autotable')])
      const doc = new jsPDF()
      const W = doc.internal.pageSize.getWidth()
      doc.setFillColor(0, 70, 127); doc.rect(0, 0, W, 34, 'F')
      doc.setTextColor(255, 255, 255); doc.setFontSize(18); doc.setFont('helvetica', 'bold')
      doc.text('JURY-AI Full Legal Analysis Report', 14, 14)
      doc.setFontSize(9); doc.setFont('helvetica', 'normal')
      doc.text(`File: ${data.filename}    Score: ${data.score}/100 — ${scoreLabel}`, 14, 23)
      doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30)
      const sc = data.score
      const col = sc >= 80 ? [16, 185, 129] : sc >= 50 ? [251, 191, 36] : [244, 63, 94]
      doc.setFillColor(220, 220, 220); doc.rect(14, 38, 182, 5, 'F')
      doc.setFillColor(...col); doc.rect(14, 38, (sc / 100) * 182, 5, 'F')
      let y = 52
      if (data.summary) {
        doc.setFont('helvetica', 'bold'); doc.setFontSize(12); doc.setTextColor(30, 30, 30); doc.text('Document Summary', 14, y); y += 6
        doc.setFont('helvetica', 'normal'); doc.setFontSize(9)
        const lines = doc.splitTextToSize(data.summary, 182); doc.text(lines, 14, y); y += lines.length * 5 + 8
      }
      if (data.entities) {
        const rows = []
        if (data.entities.parties?.length) rows.push(['Parties', data.entities.parties.join(', ')])
        if (data.entities.dates?.length) rows.push(['Key Dates', data.entities.dates.join(', ')])
        if (data.entities.amounts?.length) rows.push(['Amounts', data.entities.amounts.join(', ')])
        if (data.entities.jurisdictions?.length) rows.push(['Jurisdiction', data.entities.jurisdictions.join(', ')])
        if (rows.length) {
          autoTable(doc, { startY: y, head: [['Entity', 'Details']], body: rows, theme: 'grid', headStyles: { fillColor: [0, 70, 127], fontSize: 9 }, styles: { fontSize: 9 }, columnStyles: { 0: { cellWidth: 45, fontStyle: 'bold' } } })
          y = doc.lastAutoTable.finalY + 10
        }
      }
      if (allClauses.length) {
        autoTable(doc, {
          startY: y, head: [['Clause', 'Risk', 'Justification', 'Safer Alternative']],
          body: allClauses.map(c => [c.clause_name, c.risk_level, c.justification, c.safer_alternative || '—']),
          theme: 'striped', headStyles: { fillColor: [0, 70, 127], fontSize: 9 },
          styles: { fontSize: 8, overflow: 'linebreak' },
          columnStyles: { 0: { cellWidth: 40 }, 1: { cellWidth: 18 }, 2: { cellWidth: 62 }, 3: { cellWidth: 62 } },
        })
      }
      const pages = doc.internal.getNumberOfPages()
      for (let i = 1; i <= pages; i++) {
        doc.setPage(i); doc.setFontSize(8); doc.setTextColor(150)
        doc.text('JURY-AI | DSATM, Bengaluru', 14, doc.internal.pageSize.getHeight() - 8)
        doc.text(`Page ${i} of ${pages}`, W - 28, doc.internal.pageSize.getHeight() - 8)
      }
      doc.save(`JURY-AI-Full-Report-${(data.filename || 'report').replace(/\.[^/.]+$/, '')}.pdf`)
    } catch (e) { console.error(e) }
  }

  return (
    <div className="min-h-screen bg-midnight-dark text-slate-200 font-sans">
      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="sticky top-0 z-10 glass-panel border-b border-white/10 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => router.push('/')} className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm">
            <ArrowLeft className="w-4 h-4" /> Dashboard
          </button>
          <div className="w-px h-5 bg-white/10" />
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-cyber-cyan" />
            <span className="font-bold text-white">JURY-AI</span>
            <span className="text-slate-400 text-sm">/ Full Analysis Report</span>
          </div>
        </div>
        <button onClick={downloadPDF} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyber-cyan/10 hover:bg-cyber-cyan/20 border border-cyber-cyan/30 text-cyber-cyan text-sm font-mono transition-all">
          <Download className="w-4 h-4" /> Download PDF
        </button>
      </div>

      <div className="max-w-6xl mx-auto px-8 py-8 space-y-6">

        {/* ── Hero Score Banner ───────────────────────────────────────────── */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="glass-panel rounded-2xl p-8 flex items-center gap-8">
          <div className="relative w-40 h-40 flex-shrink-0">
            <svg className="-rotate-90 w-full h-full" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="50" stroke="rgba(255,255,255,0.08)" strokeWidth="10" fill="none" />
              <motion.circle cx="60" cy="60" r="50" stroke={scoreColor} strokeWidth="10" fill="none" strokeLinecap="round"
                initial={{ strokeDasharray: 314, strokeDashoffset: 314 }}
                animate={{ strokeDashoffset: 314 - (data.score / 100) * 314 }}
                transition={{ duration: 1.5, ease: 'easeOut' }} />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-5xl font-bold text-white">{data.score}</span>
              <span className="text-xs text-slate-400 font-mono">/ 100</span>
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl font-bold text-white">{data.filename}</span>
              <span className="px-3 py-1 rounded-full text-xs font-bold font-mono" style={{ background: `${scoreColor}22`, color: scoreColor, border: `1px solid ${scoreColor}44` }}>
                {scoreLabel}
              </span>
            </div>
            <p className="text-slate-400 text-sm mb-4">Analysed {new Date(data.date).toLocaleString()}</p>
            <div className="flex flex-wrap gap-2">
              {nCrit > 0 && <span className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-mono">{nCrit} Critical</span>}
              {nHigh > 0 && <span className="px-3 py-1.5 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 text-xs font-mono">{nHigh} High</span>}
              {nMed > 0 && <span className="px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-mono">{nMed} Medium</span>}
              {nLow > 0 && <span className="px-3 py-1.5 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400 text-xs font-mono">{nLow} Low</span>}
            </div>
          </div>
        </motion.div>

        {/* ── Summary + Charts row ────────────────────────────────────────── */}
        <div className="grid grid-cols-3 gap-4">
          {data.summary && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
              className="col-span-2 glass-panel rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-3"><FileText className="w-4 h-4 text-cyber-cyan" /><h2 className="font-semibold text-white">Document Summary</h2></div>
              <p className="text-slate-300 text-sm leading-relaxed">{data.summary}</p>
            </motion.div>
          )}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
            className="glass-panel rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-3"><BarChart2 className="w-4 h-4 text-cyber-cyan" /><h2 className="font-semibold text-white">Distribution</h2></div>
            <ResponsiveContainer width="100%" height={140}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={38} outerRadius={55} paddingAngle={3} dataKey="value">
                  {pieData.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '12px', color: '#e2e8f0' }} />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* ── Named Entities ──────────────────────────────────────────────── */}
        {data.entities && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="glass-panel rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4"><Users className="w-4 h-4 text-cyber-cyan" /><h2 className="font-semibold text-white">Named Entities</h2></div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {entitySections.map(({ key, label, Icon, color, bg }) => {
                const items = data.entities?.[key] || []
                if (!items.length) return null
                return (
                  <div key={key} className={`p-4 rounded-xl border ${bg}`}>
                    <div className={`flex items-center gap-2 mb-2 ${color}`}><Icon className="w-4 h-4" /><span className="text-xs font-semibold uppercase tracking-wide">{label}</span></div>
                    <div className="space-y-1">
                      {items.map((item, i) => <p key={i} className="text-xs text-slate-300 truncate">{item}</p>)}
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}

        {/* ── All Clauses Table ───────────────────────────────────────────── */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="glass-panel rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4"><ShieldAlert className="w-4 h-4 text-cyber-cyan" /><h2 className="font-semibold text-white">Clause-by-Clause Analysis</h2><span className="text-xs text-slate-500 ml-1">({allClauses.length} clauses identified)</span></div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-left">
                  <th className="pb-3 pr-4 text-xs font-semibold text-slate-400 uppercase tracking-wide">Clause</th>
                  <th className="pb-3 pr-4 text-xs font-semibold text-slate-400 uppercase tracking-wide w-24">Risk</th>
                  <th className="pb-3 pr-4 text-xs font-semibold text-slate-400 uppercase tracking-wide">Justification</th>
                  <th className="pb-3 text-xs font-semibold text-slate-400 uppercase tracking-wide">Safer Alternative</th>
                </tr>
              </thead>
              <tbody>
                {allClauses.map((clause, i) => {
                  const rl = clause.risk_level?.toLowerCase()
                  const colors = { critical: 'text-red-400 bg-red-500/10 border-red-500/30', high: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30', medium: 'text-blue-400 bg-blue-500/10 border-blue-500/30', low: 'text-green-400 bg-green-500/10 border-green-500/30' }
                  const c = colors[rl] || colors.low
                  return (
                    <tr key={i} className="border-b border-white/5 hover:bg-white/3 transition-colors">
                      <td className="py-3 pr-4 font-medium text-white">{clause.clause_name}</td>
                      <td className="py-3 pr-4">
                        <span className={`px-2 py-1 rounded-md text-[11px] font-mono border ${c}`}>{clause.risk_level}</span>
                      </td>
                      <td className="py-3 pr-4 text-slate-300 text-xs leading-relaxed">{clause.justification}</td>
                      <td className="py-3 text-xs leading-relaxed">
                        {clause.safer_alternative ? (
                          <div className="flex items-start gap-1.5">
                            <CheckCircle className="w-3.5 h-3.5 text-green-400 flex-shrink-0 mt-0.5" />
                            <span className="text-green-300">{clause.safer_alternative}</span>
                          </div>
                        ) : <span className="text-slate-600">—</span>}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* ── Risk Bar Chart ──────────────────────────────────────────────── */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="glass-panel rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4"><BarChart2 className="w-4 h-4 text-cyber-cyan" /><h2 className="font-semibold text-white">Risk Level Breakdown</h2></div>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={barData} barSize={40}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#e2e8f0' }} />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {barData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* ── Q&A Log ────────────────────────────────────────────────────── */}
        {data.messages?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
            className="glass-panel rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-4 h-4 text-cyber-cyan" /><h2 className="font-semibold text-white">Legal Q&A Log</h2>
            </div>
            <div className="space-y-3">
              {data.messages.map((m, i) => (
                <div key={i} className={`p-4 rounded-xl text-sm leading-relaxed ${m.role === 'user' ? 'bg-cyan-500/10 border border-cyan-500/20 text-cyan-100' : 'bg-white/5 border border-white/10 text-slate-200'}`}>
                  <span className="text-[10px] font-mono uppercase tracking-wider opacity-60 block mb-1">{m.role === 'user' ? 'Question' : 'AI Answer'}</span>
                  {m.content}
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Footer */}
        <div className="text-center py-4 text-xs text-slate-600 font-mono">
          JURY-AI · Dayananda Sagar Academy of Technology and Management · Legal Intelligence Platform
        </div>
      </div>
    </div>
  )
}
