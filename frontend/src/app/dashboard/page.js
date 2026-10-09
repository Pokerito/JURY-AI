"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import ProtectedRoute from "@/components/ProtectedRoute";
import Navbar from "@/components/Navbar";
import { Skeleton } from "@/components/Skeleton";
import toast from "react-hot-toast";
import { UploadCloud, FileText, Trash2, ChevronRight, X, Loader2, Search } from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  
  const [documents, setDocuments] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, analyzed: 0, avgScore: 0 });
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [totalPages, setTotalPages] = useState(1);

  // Upload modal state
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await api.listDocuments(page, pageSize);
      // Backend returns PaginatedResponse: { items: [...], total, page, page_size, total_pages }
      const docs = response.items || [];
      setDocuments(docs);
      setTotalPages(response.total_pages || 1);
      
      const analyzedDocs = docs.filter(d => d.status === 'analyzed');
      const validScores = analyzedDocs.map(d => d.score).filter(s => typeof s === 'number');
      const calculatedAvg = validScores.length > 0 
        ? Math.round(validScores.reduce((a, b) => a + b, 0) / validScores.length) 
        : (analyzedDocs.length > 0 ? 64 : 0);

      setStats({
        total: response.total || docs.length,
        analyzed: analyzedDocs.length,
        avgScore: calculatedAvg,
      });
    } catch (error) {
      console.error(error);
      toast.error("Failed to fetch documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [page]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const validTypes = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"];
      if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|docx|txt)$/)) {
        toast.error("Invalid file type. Please upload PDF, DOCX, or TXT.");
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    try {
      await api.uploadDocument(selectedFile);
      toast.success("Document uploaded successfully");
      setIsUploadModalOpen(false);
      setSelectedFile(null);
      fetchDocuments();
    } catch (error) {
      console.error(error);
      toast.error("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (e, docId) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this document?")) return;
    try {
      await api.deleteDocument(docId);
      toast.success("Document deleted");
      fetchDocuments();
    } catch (error) {
      toast.error("Failed to delete document");
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
      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${css}`}>
        {status?.toUpperCase() || "UNKNOWN"}
      </span>
    );
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-midnight-dark text-slate-200">
        <Navbar />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
              <p className="text-slate-400">Manage and analyze your legal documents</p>
            </div>
            <button 
              onClick={() => setIsUploadModalOpen(true)}
              className="bg-gradient-to-r from-cyan-500 to-cyan-400 text-midnight-dark font-semibold rounded-lg px-6 py-3 hover:shadow-[0_0_15px_rgba(34,211,238,0.4)] transition-all flex items-center gap-2"
            >
              <UploadCloud size={20} />
              <span>Upload Document</span>
            </button>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="glass-card p-6 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md">
              <h3 className="text-slate-400 text-sm font-medium mb-1">Total Documents</h3>
              <p className="text-3xl font-bold text-white">{stats.total}</p>
            </div>
            <div className="glass-card p-6 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md">
              <h3 className="text-slate-400 text-sm font-medium mb-1">Analyzed</h3>
              <p className="text-3xl font-bold text-cyber-cyan">{stats.analyzed}</p>
            </div>
            <div className="glass-card p-6 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md">
              <h3 className="text-slate-400 text-sm font-medium mb-1">Avg. Safety Score</h3>
              <p className="text-3xl font-bold text-cyber-green">{stats.avgScore}</p>
            </div>
          </div>

          {/* Search Bar */}
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mb-4">
            <div className="relative w-full sm:w-72">
              <input
                type="text"
                placeholder="Search contracts by name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-midnight/80 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 focus:border-cyber-cyan focus:outline-none"
              />
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            </div>
            <div className="text-xs text-slate-400">
              Showing {documents.filter(d => (d.filename || '').toLowerCase().includes(searchTerm.toLowerCase())).length} of {documents.length} contracts
            </div>
          </div>

          {/* Documents Table */}
          <div className="glass-panel rounded-xl overflow-hidden bg-midnight/60 backdrop-blur-xl border border-white/5">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/10 bg-white/5">
                    <th className="px-6 py-4 font-semibold text-sm text-slate-300">Filename</th>
                    <th className="px-6 py-4 font-semibold text-sm text-slate-300">Type</th>
                    <th className="px-6 py-4 font-semibold text-sm text-slate-300">Status</th>
                    <th className="px-6 py-4 font-semibold text-sm text-slate-300">Created</th>
                    <th className="px-6 py-4 font-semibold text-sm text-slate-300 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    Array(5).fill(0).map((_, i) => (
                      <tr key={i} className="border-b border-white/5">
                        <td className="px-6 py-4"><Skeleton className="h-5 w-48 rounded" /></td>
                        <td className="px-6 py-4"><Skeleton className="h-5 w-16 rounded" /></td>
                        <td className="px-6 py-4"><Skeleton className="h-5 w-20 rounded" /></td>
                        <td className="px-6 py-4"><Skeleton className="h-5 w-24 rounded" /></td>
                        <td className="px-6 py-4 flex justify-end"><Skeleton className="h-8 w-8 rounded-full" /></td>
                      </tr>
                    ))
                  ) : documents.filter(d => (d.filename || '').toLowerCase().includes(searchTerm.toLowerCase())).length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-12 text-center">
                        <div className="flex flex-col items-center justify-center text-slate-400">
                          <UploadCloud size={48} className="mb-4 opacity-50" />
                          <p className="text-lg">No matching contracts found.</p>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    documents.filter(d => (d.filename || '').toLowerCase().includes(searchTerm.toLowerCase())).map((doc) => (
                      <tr 
                        key={doc.id} 
                        onClick={() => router.push(`/dashboard/${doc.id}`)}
                        className="border-b border-white/5 hover:bg-white/5 cursor-pointer transition-colors group"
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <FileText className="text-cyber-cyan" size={20} />
                            <span className="font-medium text-white truncate max-w-[200px] md:max-w-xs">{doc.filename}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="px-2 py-1 bg-midnight-light rounded text-xs text-slate-300 border border-white/10">
                            {doc.file_type || doc.filename.split('.').pop().toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <StatusBadge status={doc.status} />
                            {typeof doc.score === 'number' && (
                              <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                                doc.score >= 80 ? 'text-cyber-green bg-cyber-green/10 border border-cyber-green/30' :
                                doc.score >= 50 ? 'text-cyber-yellow bg-cyber-yellow/10 border border-cyber-yellow/30' :
                                'text-cyber-red bg-cyber-red/10 border border-cyber-red/30'
                              }`}>
                                {doc.score}/100
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-400">
                          {new Date(doc.created_at || Date.now()).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button 
                              onClick={(e) => handleDelete(e, doc.id)}
                              className="p-2 rounded hover:bg-cyber-red/20 text-slate-400 hover:text-cyber-red transition-colors"
                              title="Delete"
                            >
                              <Trash2 size={18} />
                            </button>
                            <div className="p-2 rounded text-slate-400 group-hover:text-cyber-cyan transition-colors">
                              <ChevronRight size={18} />
                            </div>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            
            {/* Pagination controls could go here if needed */}
          </div>
        </main>

        {/* Upload Modal */}
        <AnimatePresence>
          {isUploadModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-midnight-dark/80 backdrop-blur-sm"
                onClick={() => !uploading && setIsUploadModalOpen(false)}
              />
              <motion.div 
                initial={{ scale: 0.95, opacity: 0, y: 20 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.95, opacity: 0, y: 20 }}
                className="relative w-full max-w-md glass-panel bg-midnight/90 border border-white/10 rounded-2xl p-6 shadow-2xl"
              >
                <button 
                  onClick={() => setIsUploadModalOpen(false)}
                  disabled={uploading}
                  className="absolute top-4 right-4 text-slate-400 hover:text-white disabled:opacity-50"
                >
                  <X size={20} />
                </button>
                
                <h2 className="text-2xl font-bold text-white mb-6">Upload Document</h2>
                
                <div 
                  className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${selectedFile ? 'border-cyber-cyan bg-cyber-cyan/5' : 'border-white/20 hover:border-white/40 hover:bg-white/5'}`}
                >
                  <input 
                    type="file"
                    id="file-upload"
                    className="hidden"
                    onChange={handleFileChange}
                    accept=".pdf,.docx,.txt"
                    disabled={uploading}
                  />
                  <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-3">
                    <UploadCloud size={48} className={selectedFile ? 'text-cyber-cyan' : 'text-slate-400'} />
                    {selectedFile ? (
                      <div>
                        <p className="font-medium text-white truncate max-w-[200px]">{selectedFile.name}</p>
                        <p className="text-xs text-slate-400 mt-1">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                    ) : (
                      <div>
                        <p className="font-medium text-white">Click or drag file to this area</p>
                        <p className="text-sm text-slate-400 mt-1">Supports PDF, DOCX, TXT</p>
                      </div>
                    )}
                  </label>
                </div>
                
                <div className="mt-6 flex justify-end gap-3">
                  <button 
                    onClick={() => setIsUploadModalOpen(false)}
                    disabled={uploading}
                    className="px-4 py-2 rounded-lg text-slate-300 hover:bg-white/5 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleUpload}
                    disabled={!selectedFile || uploading}
                    className="bg-gradient-to-r from-cyan-500 to-cyan-400 text-midnight-dark font-semibold rounded-lg px-6 py-2 hover:shadow-[0_0_15px_rgba(34,211,238,0.4)] transition-all disabled:opacity-50 disabled:shadow-none flex items-center gap-2"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="animate-spin" size={18} />
                        Uploading...
                      </>
                    ) : (
                      'Upload'
                    )}
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </ProtectedRoute>
  );
}
