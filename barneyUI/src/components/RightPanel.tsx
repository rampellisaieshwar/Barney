import React, { useEffect, useState } from 'react';
import { MoreHorizontal, Brain, Zap, ShieldCheck, BookOpen, ExternalLink } from 'lucide-react';
import { cn } from '../lib/utils';
import { KnowledgeEntry } from '../types';
import { api } from '../services/api';
import { motion, AnimatePresence } from 'motion/react';

interface RightPanelProps {
  theme: 'light' | 'dark';
}

export const RightPanel: React.FC<RightPanelProps> = ({ theme }) => {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLedger = async () => {
      const data = await api.getKnowledgeLedger();
      setEntries(data);
      setLoading(false);
    };
    fetchLedger();
  }, []);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'pattern': return <Zap className="w-3 h-3 text-blue-500" />;
      case 'constraint': return <ShieldCheck className="w-3 h-3 text-orange-500" />;
      case 'fact': return <BookOpen className="w-3 h-3 text-green-500" />;
      default: return <Brain className="w-3 h-3 text-gray-500" />;
    }
  };

  return (
    <div className={cn(
      "w-72 h-screen flex flex-col p-6 border-l transition-colors duration-300",
      theme === 'light' ? "bg-white border-gray-200" : "bg-[#090B1E] border-white/5"
    )}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-azure-radiance" />
          <h3 className={cn("text-sm font-bold", theme === 'light' ? "text-black" : "text-white")}>
            Memory & Insights
          </h3>
        </div>
        <button className="opacity-30 hover:opacity-100 transition-opacity">
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto custom-scrollbar pr-1">
        {loading ? (
          [1, 2, 3, 4].map(i => (
            <div key={i} className={cn(
              "h-24 rounded-2xl animate-pulse",
              theme === 'light' ? "bg-gray-100" : "bg-white/5"
            )} />
          ))
        ) : (
          <AnimatePresence mode="popLayout">
            {entries.map((entry, idx) => (
              <motion.div 
                key={entry.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className={cn(
                  "p-4 rounded-2xl border transition-all cursor-pointer group relative",
                  theme === 'light' 
                    ? "bg-[#F9FAFC] border-gray-100 hover:border-azure-radiance/30" 
                    : "bg-white/5 border-white/5 hover:border-white/20 backdrop-blur-sm"
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className={cn(
                    "px-2 py-0.5 rounded-full border text-[8px] font-bold uppercase tracking-widest flex items-center gap-1.5",
                    theme === 'light' ? "bg-white border-gray-100" : "bg-white/5 border-white/10"
                  )}>
                    {getCategoryIcon(entry.category)}
                    {entry.category}
                  </div>
                  <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-30 transition-opacity" />
                </div>
                <p className={cn(
                  "text-[11px] leading-relaxed line-clamp-3 font-medium",
                  theme === 'light' ? "text-black/80" : "text-white/80"
                )}>
                  {entry.content}
                </p>
                <div className="mt-3 flex items-center justify-between opacity-30">
                  <span className="text-[9px] font-bold uppercase tracking-widest truncate max-w-[100px]">
                    {entry.source}
                  </span>
                  <span className="text-[9px] font-mono">
                    {new Date(entry.timestamp).toLocaleDateString()}
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>

      <div className="mt-6 pt-6 border-t border-white/5">
        <div className={cn(
          "p-4 rounded-2xl border flex flex-col items-center text-center gap-2",
          theme === 'light' ? "bg-azure-radiance/5 border-azure-radiance/10" : "bg-azure-radiance/10 border-azure-radiance/20"
        )}>
          <div className="w-8 h-8 rounded-full bg-azure-radiance flex items-center justify-center shadow-lg shadow-azure-radiance/20">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <p className={cn("text-[10px] font-bold uppercase tracking-widest", theme === 'light' ? "text-azure-radiance" : "text-white")}>
            Neural Indexing Active
          </p>
        </div>
      </div>
    </div>
  );
};
