"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import ProtectedRoute from "@/components/ProtectedRoute";
import Navbar from "@/components/Navbar";
import { Skeleton } from "@/components/Skeleton";
import SafetyGauge from "@/components/SafetyGauge";
import RiskClauseCard from "@/components/RiskClauseCard";
import toast from "react-hot-toast";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { 
  ChevronRight, ArrowLeft, FileText, Loader2, Play, Users, Calendar, DollarSign, Scale, MessageSquare, Send
} from "lucide-react";

export default function DocumentDetailPage() {
  const router = useRouter();
  const routeParams = useParams();
  const docId = routeParams?.docId;
  
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  
  // Analysis Data
  const [riskData, setRiskData] = useState(null);
  const [summary, setSummary] = useState(null);
  const [entities, setEntities] = useState(null);
  const [loadingSections, setLoadingSections] = useState({
    risk: false,
    summary: false,
    entities: false
  });

  // Chat
  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', content: 'Hello! You can ask me questions about this document.' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  const fetchDocumentData = async () => {
    setLoading(true);
    try {
      const docData = await api.getDocument(docId);
      setDoc(docData);
      fetchAllAnalysis();
    } catch (error) {
      console.error(error);
      toast.error("Failed to load document");
    } finally {
      setLoading(false);
    }
  };

  const fetchAllAnalysis = async () => {
    setLoadingSections({ risk: true, summary: true, entities: true });
    
    // Fetch Risk Score
    try {
      const risk = await api.getRiskScore(docId);
      setRiskData(risk);
    } catch (e) {
      console.error(e);
      toast.error("Failed to load risk analysis");
    } finally {
      setLoadingSections(prev => ({ ...prev, risk: false }));
    }

    // Fetch Summary
    try {
      const sum = await api.getSummary(docId);
      setSummary(sum);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSections(prev => ({ ...prev, summary: false }));
    }

    // Fetch Entities
    try {
      const ent = await api.getEntities(docId);
      setEntities(ent);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSections(prev => ({ ...prev, entities: false }));
    }
  };

  useEffect(() => {
    if (docId) fetchDocumentData();
  }, [docId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      await api.triggerAnalysis(docId);
      toast.success("Analysis complete!");
      await fetchAllAnalysis();
    } catch (error) {
      console.error(error);
      toast.error("Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const userMessage = chatInput.trim();
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await api.queryDocument(docId, userMessage);
      setChatMessages(prev => [...prev, { role: 'assistant', content: response.answer || response }]);
    } catch (error) {
      toast.error("Failed to get answer");
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const StatusBadge = ({ status }) => {
    const statusConfig = {
      uploaded: "bg-cyber-yellow/20 text-cyber-yellow border-cyber-yellow/30",
      processing: "bg-cyber-cyan/20 text-cyber-cyan border-cyber-cyan/30 animate-pulse",
      analyzed: "bg-cyber-green/20 text-cyber-green border-cyber-green/30",
      failed: "bg-cyber-red/20 text-cyber-red border-cyber-red/30",
    };
    const css = statusConfig[status?.toLowerCase()] || "bg-gray-500/20 text-gray-400";
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${css}`}>
        {status?.toUpperCase() || "UNKNOWN"}
      </span>
    );
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-midnight-dark text-slate-200">
          <Navbar />
          <main className="max-w-7xl mx-auto px-4 py-8">
            <Skeleton className="h-8 w-64 mb-8 rounded" />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <Skeleton className="h-[500px] rounded-xl" />
              <Skeleton className="h-[500px] rounded-xl" />
            </div>
          </main>
        </div>
      </ProtectedRoute>
    );
  }

  // Prep Recharts data
  let riskChartData = [];
  if (riskData?.all_clauses) {
    const counts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
    riskData.all_clauses.forEach(c => {
      if (counts[c.risk_level] !== undefined) counts[c.risk_level]++;
    });
    riskChartData = [
      { name: 'Critical', count: counts.Critical, fill: '#F43F5E' },
      { name: 'High', count: counts.High, fill: '#f97316' },
      { name: 'Medium', count: counts.Medium, fill: '#FBBF24' },
      { name: 'Low', count: counts.Low, fill: '#10B981' }
    ];
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-midnight-dark text-slate-200">
        <Navbar />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <button 
            onClick={() => router.push('/dashboard')}
            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-6"
          >
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>

          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                <FileText className="text-cyber-cyan" size={28} />
                {doc?.filename || "Document Details"}
              </h1>
              <div className="flex items-center gap-4 text-sm text-slate-400">
                <span>{doc?.file_type?.toUpperCase()}</span>
                <span>•</span>
                <span>{doc?.file_size ? `${(doc.file_size/1024).toFixed(1)} KB` : 'Unknown size'}</span>
                <span>•</span>
                <span>Uploaded {new Date(doc?.created_at || Date.now()).toLocaleDateString()}</span>
              </div>
            </div>
            <div>
              <StatusBadge status={doc?.status} />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* LEFT COLUMN */}
            <div className="space-y-8">
              
              {/* Actions & Info */}
              <div className="glass-panel p-6 rounded-xl border border-white/5 bg-midnight/60">
                {doc?.status !== 'analyzed' ? (
                  <div className="text-center py-8">
                    <h3 className="text-xl font-medium text-white mb-4">Ready for Analysis</h3>
                    <button 
                      onClick={handleAnalyze}
                      disabled={analyzing || doc?.status === 'processing'}
                      className="bg-gradient-to-r from-cyan-500 to-cyan-400 text-midnight-dark font-semibold rounded-lg px-8 py-3 hover:shadow-glow-cyan transition-all disabled:opacity-50 flex items-center gap-2 mx-auto"
                    >
                      {analyzing || doc?.status === 'processing' ? (
                        <><Loader2 className="animate-spin" size={20} /> Processing...</>
                      ) : (
                        <><Play size={20} /> Run Full Analysis</>
                      )}
                    </button>
                  </div>
                ) : (
                  <div className="text-center text-cyber-green flex items-center justify-center gap-2 py-4">
                    <FileText size={20} />
                    <span className="font-semibold">Analysis Complete</span>
                  </div>
                )}
              </div>

              {/* Safety Score Section */}
              {doc?.status === 'analyzed' && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass-panel p-6 rounded-xl border border-white/5 bg-midnight/60"
                >
                  <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <Scale className="text-cyber-cyan" /> 
                    Safety Score & Risk
                  </h3>
                  
                  {loadingSections.risk ? (
                    <div className="flex justify-center py-12"><Loader2 className="animate-spin text-cyber-cyan" size={40} /></div>
                  ) : riskData ? (
                    <div>
                      <div className="flex justify-center mb-8">
                        <SafetyGauge score={riskData.score || 85} size={220} />
                      </div>
                      
                      <div className="h-[200px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={riskChartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                            <XAxis dataKey="name" stroke="#94a3b8" tickLine={false} axisLine={false} />
                            <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} allowDecimals={false} />
                            <Tooltip 
                              cursor={{fill: '#ffffff05'}}
                              contentStyle={{ backgroundColor: '#0B1120', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                            />
                            <Bar dataKey="count" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  ) : (
                    <p className="text-slate-400">Risk data not available.</p>
                  )}
                </motion.div>
              )}

              {/* Risk Clauses Section */}
              {doc?.status === 'analyzed' && riskData?.all_clauses && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="space-y-4"
                >
                  <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <FileText className="text-cyber-yellow" /> 
                    Identified Clauses
                  </h3>
                  
                  {riskData.all_clauses
                    .sort((a, b) => {
                      const order = { Critical: 0, High: 1, Medium: 2, Low: 3 };
                      return (order[a.risk_level] ?? 4) - (order[b.risk_level] ?? 4);
                    })
                    .map((clause, idx) => (
                      <RiskClauseCard key={idx} {...clause} />
                  ))}
                </motion.div>
              )}
            </div>

            {/* RIGHT COLUMN */}
            <div className="space-y-8 flex flex-col">
              
              {/* Summary Section */}
              {doc?.status === 'analyzed' && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="glass-panel p-6 rounded-xl border border-white/5 bg-midnight/60"
                >
                  <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <FileText className="text-cyber-cyan" /> 
                    AI Summary
                  </h3>
                  
                  {loadingSections.summary ? (
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-5/6" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-4/6" />
                    </div>
                  ) : (
                    <div className="glass-card p-4 rounded-lg text-slate-300 leading-relaxed text-sm">
                      {summary?.summary || summary || "No summary available."}
                    </div>
                  )}
                </motion.div>
              )}

              {/* Entities Section */}
              {doc?.status === 'analyzed' && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <Users className="text-cyber-cyan" /> 
                    Extracted Entities
                  </h3>
                  
                  {loadingSections.entities ? (
                    <div className="grid grid-cols-2 gap-4">
                      <Skeleton className="h-24 rounded-lg" />
                      <Skeleton className="h-24 rounded-lg" />
                      <Skeleton className="h-24 rounded-lg" />
                      <Skeleton className="h-24 rounded-lg" />
                    </div>
                  ) : entities && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="glass-card p-4 rounded-lg border border-white/5">
                        <div className="flex items-center gap-2 text-cyber-cyan mb-2">
                          <Users size={16} /> <span className="font-medium text-sm">Parties</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {entities.parties?.length ? entities.parties.map((e, i) => (
                            <span key={i} className="text-xs bg-midnight-light px-2 py-1 rounded text-slate-300">{e}</span>
                          )) : <span className="text-xs text-slate-500">None found</span>}
                        </div>
                      </div>
                      
                      <div className="glass-card p-4 rounded-lg border border-white/5">
                        <div className="flex items-center gap-2 text-cyber-yellow mb-2">
                          <Calendar size={16} /> <span className="font-medium text-sm">Dates</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {entities.dates?.length ? entities.dates.map((e, i) => (
                            <span key={i} className="text-xs bg-midnight-light px-2 py-1 rounded text-slate-300">{e}</span>
                          )) : <span className="text-xs text-slate-500">None found</span>}
                        </div>
                      </div>

                      <div className="glass-card p-4 rounded-lg border border-white/5">
                        <div className="flex items-center gap-2 text-cyber-green mb-2">
                          <DollarSign size={16} /> <span className="font-medium text-sm">Amounts</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {entities.amounts?.length ? entities.amounts.map((e, i) => (
                            <span key={i} className="text-xs bg-midnight-light px-2 py-1 rounded text-slate-300">{e}</span>
                          )) : <span className="text-xs text-slate-500">None found</span>}
                        </div>
                      </div>

                      <div className="glass-card p-4 rounded-lg border border-white/5">
                        <div className="flex items-center gap-2 text-slate-300 mb-2">
                          <Scale size={16} /> <span className="font-medium text-sm">Jurisdiction</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {entities.jurisdictions?.length ? entities.jurisdictions.map((e, i) => (
                            <span key={i} className="text-xs bg-midnight-light px-2 py-1 rounded text-slate-300">{e}</span>
                          )) : <span className="text-xs text-slate-500">None found</span>}
                        </div>
                      </div>
                    </div>
                  )}
                </motion.div>
              )}

              {/* RAG Chat Section */}
              {doc?.status === 'analyzed' && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="glass-panel rounded-xl border border-white/5 bg-midnight/60 flex flex-col h-[500px]"
                >
                  <div className="p-4 border-b border-white/10 flex items-center gap-2">
                    <MessageSquare className="text-cyber-cyan" />
                    <h3 className="font-bold text-white">Document Q&A</h3>
                  </div>
                  
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {chatMessages.map((msg, idx) => (
                      <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-xl p-3 text-sm ${
                          msg.role === 'user' 
                            ? 'bg-cyber-cyan text-midnight-dark font-medium' 
                            : 'glass-card text-slate-200 border border-white/5'
                        }`}>
                          {msg.content}
                        </div>
                      </div>
                    ))}
                    {chatLoading && (
                      <div className="flex justify-start">
                        <div className="glass-card rounded-xl p-3 flex items-center gap-2">
                          <Loader2 className="animate-spin text-cyber-cyan" size={16} />
                          <span className="text-xs text-slate-400">AI is thinking...</span>
                        </div>
                      </div>
                    )}
                    <div ref={chatEndRef} />
                  </div>

                  <form onSubmit={handleChatSubmit} className="p-4 border-t border-white/10 flex gap-2">
                    <input 
                      type="text" 
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      placeholder="Ask something about this contract..."
                      className="flex-1 bg-midnight-light border border-white/10 focus:border-cyber-cyan rounded-lg px-4 py-2 text-sm text-slate-200 outline-none"
                    />
                    <button 
                      type="submit"
                      disabled={!chatInput.trim() || chatLoading}
                      className="bg-cyber-cyan text-midnight-dark p-2 rounded-lg hover:shadow-glow-cyan disabled:opacity-50 transition-all flex items-center justify-center w-10"
                    >
                      <Send size={16} />
                    </button>
                  </form>
                </motion.div>
              )}

            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
