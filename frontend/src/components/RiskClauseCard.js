"use client";
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, ChevronDown, ChevronUp, CheckCircle } from "lucide-react";

export default function RiskClauseCard({ 
  clause_name, 
  risk_level = "Low", 
  justification, 
  safer_alternative 
}) {
  const [expanded, setExpanded] = useState(false);

  const colors = {
    Critical: { border: "border-cyber-red", bg: "bg-cyber-red/10", text: "text-cyber-red" },
    High: { border: "border-orange-500", bg: "bg-orange-500/10", text: "text-orange-500" },
    Medium: { border: "border-cyber-yellow", bg: "bg-cyber-yellow/10", text: "text-cyber-yellow" },
    Low: { border: "border-cyber-green", bg: "bg-cyber-green/10", text: "text-cyber-green" },
  };

  const theme = colors[risk_level] || colors.Low;

  return (
    <motion.div 
      whileHover={{ scale: 1.01 }}
      className={`glass-card rounded-lg overflow-hidden border-l-4 ${theme.border} border-y border-r border-white/5 bg-white/5 transition-all`}
    >
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h4 className="font-semibold text-white text-base pr-4">{clause_name}</h4>
          <span className={`px-2.5 py-1 rounded-full text-xs font-bold whitespace-nowrap ${theme.bg} ${theme.text}`}>
            {risk_level.toUpperCase()}
          </span>
        </div>
        
        <p className="text-slate-300 text-sm leading-relaxed mb-3">
          {justification}
        </p>

        {safer_alternative && (
          <div>
            <button 
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 text-xs font-medium text-cyber-cyan hover:text-cyan-300 transition-colors"
            >
              {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              {expanded ? "Hide Safer Alternative" : "View Safer Alternative"}
            </button>
            
            <AnimatePresence>
              {expanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden mt-3"
                >
                  <div className="p-3 rounded bg-cyber-green/5 border border-cyber-green/20 text-sm text-slate-200">
                    <div className="flex items-center gap-2 text-cyber-green font-medium mb-1">
                      <CheckCircle size={14} /> Recommended Revision
                    </div>
                    {safer_alternative}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </motion.div>
  );
}
