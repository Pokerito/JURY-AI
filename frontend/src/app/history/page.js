"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import ProtectedRoute from "@/components/ProtectedRoute";
import Navbar from "@/components/Navbar";
import { 
  History, ArrowLeft, FileText, ShieldAlert, CheckCircle, 
  Calendar, Eye, Download, Search, AlertTriangle, Filter 
} from "lucide-react";
import Link from "next/link";
import { Skeleton } from "@/components/Skeleton";

export default function HistoryPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await api.listDocuments(1, 100);
      setDocuments(res.items || []);
    } catch (err) {
      console.error("Failed to load history", err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = documents.filter((doc) => {
    const matchesSearch = (doc.filename || "").toLowerCase().includes(search.toLowerCase());
    if (!matchesSearch) return false;
    if (filter === "analyzed") return doc.status === "analyzed";
    if (filter === "pending") return doc.status !== "analyzed";
    return true;
  });

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-midnight text-slate-100 flex flex-col">
        <Navbar />

        <div className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
            <div>
              <Link 
                href="/dashboard" 
                className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-cyber-cyan mb-2 transition-colors"
              >
                <ArrowLeft size={16} /> Back to Dashboard
              </Link>
              <h1 className="text-3xl font-bold text-white tracking-wide flex items-center gap-3">
                <History className="text-cyber-cyan" size={30} />
                Contract Audit History & Activity Log
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Chronological timeline of all uploaded contracts, risk classifications, and legal reports.
              </p>
            </div>
          </div>

          {/* Controls & Filter */}
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mb-6">
            <div className="relative w-full sm:w-80">
              <input
                type="text"
                placeholder="Search audit trail..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-midnight/80 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 focus:border-cyber-cyan focus:outline-none"
              />
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            </div>

            <div className="flex items-center gap-2 self-start sm:self-auto">
              <span className="text-xs text-slate-400 flex items-center gap-1 mr-1">
                <Filter size={14} /> Filter:
              </span>
              {[
                { id: "all", label: "All Logs" },
                { id: "analyzed", label: "Analyzed" },
                { id: "pending", label: "Pending" }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setFilter(tab.id)}
                  className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
                    filter === tab.id
                      ? "bg-cyber-cyan/15 text-cyber-cyan border-cyber-cyan/40 font-medium"
                      : "bg-white/5 text-slate-400 border-white/5 hover:border-white/20"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Timeline Table Card */}
          <div className="glass-panel rounded-2xl overflow-hidden bg-midnight/60 border border-white/5">
            {loading ? (
              <div className="p-8 space-y-4">
                {Array(4).fill(0).map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full rounded-xl" />
                ))}
              </div>
            ) : filtered.length === 0 ? (
              <div className="p-16 text-center text-slate-400">
                <History size={48} className="mx-auto mb-3 opacity-30 text-cyber-cyan" />
                <p className="text-lg font-medium text-slate-300">No audit records found</p>
                <p className="text-xs text-slate-500 mt-1">Upload and analyze contracts to populate your activity log.</p>
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {filtered.map((doc, idx) => (
                  <div 
                    key={doc.id}
                    className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-white/5 transition-colors"
                  >
                    <div className="flex items-start gap-4">
                      <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-cyber-cyan mt-1 md:mt-0">
                        <FileText size={22} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-white text-base hover:text-cyber-cyan transition-colors">
                          <Link href={`/dashboard/${doc.id}`}>{doc.filename}</Link>
                        </h4>
                        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1.5 font-mono">
                          <span>{doc.file_type?.toUpperCase() || "TXT"}</span>
                          <span>•</span>
                          <span>{doc.file_size ? `${(doc.file_size / 1024).toFixed(1)} KB` : "12.4 KB"}</span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <Calendar size={12} />
                            {new Date(doc.created_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 self-end md:self-center">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border ${
                        doc.status === "analyzed"
                          ? "bg-cyber-green/15 text-cyber-green border-cyber-green/30"
                          : "bg-cyber-yellow/15 text-cyber-yellow border-cyber-yellow/30"
                      }`}>
                        {doc.status || "UPLOADED"}
                      </span>

                      <Link
                        href={`/dashboard/${doc.id}`}
                        className="px-3 py-1.5 rounded-lg bg-cyber-cyan/10 hover:bg-cyber-cyan/20 border border-cyber-cyan/30 text-cyber-cyan text-xs font-medium transition-all flex items-center gap-1.5"
                      >
                        <Eye size={14} /> Open Analysis
                      </Link>

                      {doc.status === "analyzed" && (
                        <Link
                          href={`/report/${doc.id}`}
                          className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-200 text-xs font-medium transition-all flex items-center gap-1.5"
                        >
                          <Download size={14} /> Full PDF Report
                        </Link>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
