"use client";

import { useState, useEffect } from 'react';
import { Cpu, Sparkles, ChevronDown } from 'lucide-react';

export const AVAILABLE_MODELS = [
  { id: "gemini-2.5-flash", name: "Gemini 2.5 Flash", provider: "Google", badge: "Fast & Free", color: "text-cyan-400" },
  { id: "gpt-4o", name: "OpenAI GPT-4o", provider: "OpenAI", badge: "Accurate", color: "text-emerald-400" },
  { id: "gpt-4o-mini", name: "GPT-4o Mini", provider: "OpenAI", badge: "Balanced", color: "text-emerald-300" },
  { id: "claude-3-5-sonnet", name: "Claude 3.5 Sonnet", provider: "Anthropic", badge: "Best Legal Reasoning", color: "text-purple-400" },
  { id: "grok-2", name: "xAI Grok-2", provider: "xAI", badge: "Direct Risk", color: "text-amber-400" },
];

export default function ModelSelector({ selectedModel, onSelectModel }) {
  const [model, setModel] = useState(selectedModel || 'gemini-2.5-flash');

  useEffect(() => {
    const saved = localStorage.getItem('jury_ai_selected_model');
    if (saved) {
      setModel(saved);
      if (onSelectModel) onSelectModel(saved);
    }
  }, []);

  const handleChange = (e) => {
    const next = e.target.value;
    setModel(next);
    localStorage.setItem('jury_ai_selected_model', next);
    if (onSelectModel) onSelectModel(next);
  };

  const current = AVAILABLE_MODELS.find(m => m.id === model) || AVAILABLE_MODELS[0];

  return (
    <div className="flex items-center gap-2 bg-midnight-light/80 border border-white/10 px-3 py-1.5 rounded-xl shadow-sm backdrop-blur-md">
      <Sparkles className={`w-4 h-4 ${current.color}`} />
      <div className="flex flex-col">
        <span className="text-[10px] text-slate-400 font-mono leading-none">LLM ENGINE</span>
        <select
          value={model}
          onChange={handleChange}
          className="bg-transparent text-xs font-semibold text-white focus:outline-none cursor-pointer pr-2"
        >
          {AVAILABLE_MODELS.map(m => (
            <option key={m.id} value={m.id} className="bg-slate-900 text-white py-1">
              {m.name} ({m.badge})
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
