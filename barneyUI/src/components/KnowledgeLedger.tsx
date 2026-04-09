import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Database, 
  Search, 
  Filter, 
  BookOpen, 
  ShieldCheck, 
  Zap, 
  Clock,
  Tag,
  ExternalLink,
  Brain
} from 'lucide-react';
import { KnowledgeEntry } from '../types';
import { api } from '../services/api';
import { cn } from '../lib/utils';

interface KnowledgeLedgerProps {
  theme: 'light' | 'dark';
}

export const KnowledgeLedger: React.FC<KnowledgeLedgerProps> = ({ theme }) => {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

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
      case 'pattern': return <Zap className="w-4 h-4 text-blue-500" />;
      case 'constraint': return <ShieldCheck className="w-4 h-4 text-orange-500" />;
      case 'fact': return <BookOpen className="w-4 h-4 text-green-500" />;
      default: return <Database className="w-4 h-4 text-gray-500" />;
    }
  };

  const filteredEntries = entries.filter(e => 
    e.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.source.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={cn(
      "flex-1 flex flex-col h-screen transition-colors duration-300",
      theme === 'light' ? "bg-white" : "bg-[#090B1E]"
    )}>
      <header className={cn(
        "h-16 px-8 flex items-center justify-between border-b backdrop-blur-md z-10",
        theme === 'light' ? "border-gray-100 bg-white/50" : "border-white/5 bg-[#090B1E]/50"
      )}>
        <div className="flex items-center gap-3">
          <Brain className="w-5 h-5 text-azure-radiance" />
          <h2 className={cn("font-bold tracking-tight", theme === 'light' ? "text-black" : "text-white")}>Knowledge Ledger</h2>
        </div>
        <div className="flex items-center gap-4">
          <div className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl border",
            theme === 'light' ? "bg-gray-100 border-gray-200" : "bg-white/5 border-white/10"
          )}>
            <Database className="w-4 h-4 opacity-30" />
            <span className="text-[10px] font-bold uppercase tracking-widest opacity-60">Governed Knowledge Base</span>
          </div>
        </div>
      </header>

      <main className="flex-1 p-8 overflow-y-auto custom-scrollbar">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
            <div>
              <h3 className={cn("text-4xl font-bold mb-3", theme === 'light' ? "text-black" : "text-white")}>Memory & Insights</h3>
              <p className="text-gray-500 text-base max-w-2xl leading-relaxed">
                Visualizing the immutable knowledge ledger. These entries represent verified patterns and constraints used by Barney for autonomous decision making.
              </p>
            </div>
            <div className="relative w-full md:w-80">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 opacity-30" />
              <input 
                type="text" 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search ledger..." 
                className={cn(
                  "w-full rounded-xl pl-11 pr-4 py-2.5 text-sm outline-none transition-all",
                  theme === 'light' ? "bg-gray-100 border border-gray-200 focus:border-azure-radiance" : "bg-white/5 border border-white/10 focus:border-azure-radiance/50"
                )}
              />
            </div>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map(i => (
                <div key={i} className={cn(
                  "h-48 rounded-[32px] animate-pulse",
                  theme === 'light' ? "bg-gray-100" : "bg-white/5"
                )} />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <AnimatePresence mode="popLayout">
                {filteredEntries.map((entry, idx) => (
                  <motion.div
                    key={entry.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className={cn(
                      "group relative rounded-[32px] p-6 border transition-all duration-500 hover:scale-[1.02]",
                      theme === 'light' ? "bg-[#F9FAFC] border-gray-100 shadow-sm" : "bg-white/5 border-white/5 backdrop-blur-sm shadow-xl"
                    )}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className={cn(
                        "px-3 py-1 rounded-full border text-[9px] font-bold uppercase tracking-widest flex items-center gap-2",
                        theme === 'light' ? "bg-white border-gray-100" : "bg-white/5 border-white/10"
                      )}>
                        {getCategoryIcon(entry.category)}
                        {entry.category}
                      </div>
                      <div className="flex items-center gap-1.5 opacity-30">
                        <Clock className="w-3 h-3" />
                        <span className="text-[9px] font-bold uppercase tracking-widest">
                          {new Date(entry.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                    </div>

                    <p className={cn(
                      "text-sm leading-relaxed mb-6 font-medium",
                      theme === 'light' ? "text-black" : "text-white"
                    )}>
                      {entry.content}
                    </p>

                    <div className="flex items-center justify-between pt-4 border-t border-white/5">
                      <div className="flex items-center gap-2 opacity-40">
                        <Tag className="w-3 h-3" />
                        <span className="text-[10px] font-bold uppercase tracking-widest truncate max-w-[120px]">
                          {entry.source}
                        </span>
                      </div>
                      <button className="text-azure-radiance/60 hover:text-azure-radiance transition-colors">
                        <ExternalLink className="w-4 h-4" />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}

          {!loading && filteredEntries.length === 0 && (
            <div className="text-center py-20 opacity-30">
              <Database className="w-12 h-12 mx-auto mb-4" />
              <p className="text-sm font-bold uppercase tracking-widest">No matching entries found in ledger</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
