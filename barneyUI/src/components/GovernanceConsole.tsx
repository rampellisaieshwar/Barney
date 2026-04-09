import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Clock,
  Filter,
  Search,
  Activity
} from 'lucide-react';
import { PlanStep } from '../types';
import { api } from '../services/api';
import { cn } from '../lib/utils';
import { PlanVisualizer } from './PlanVisualizer';

interface GovernanceConsoleProps {
  theme: 'light' | 'dark';
}

export const GovernanceConsole: React.FC<GovernanceConsoleProps> = ({ theme }) => {
  const [pendingSteps, setPendingSteps] = useState<PlanStep[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching pending governance steps
    const fetchPending = async () => {
      // In a real app, this would be api.getPendingApprovals()
      const mockPending: PlanStep[] = [
        {
          id: 'gov-1',
          title: 'Production Database Migration',
          description: 'Applying schema changes to the production cluster.',
          status: 'pending',
          stage: 'execute',
          risk: { score: 95, level: 'critical', reasoning: 'Irreversible data modification. High risk of downtime.' },
          requiresApproval: true
        },
        {
          id: 'gov-2',
          title: 'External API Key Rotation',
          description: 'Rotating secrets for third-party service integrations.',
          status: 'pending',
          stage: 'execute',
          risk: { score: 70, level: 'high', reasoning: 'May cause temporary service interruption if propagation fails.' },
          requiresApproval: true
        }
      ];
      setPendingSteps(mockPending);
      setLoading(false);
    };
    fetchPending();
  }, []);

  const handleApprove = (id: string) => {
    setPendingSteps(prev => prev.filter(s => s.id !== id));
  };

  const handleReject = (id: string) => {
    setPendingSteps(prev => prev.filter(s => s.id !== id));
  };

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
          <ShieldCheck className="w-5 h-5 text-azure-radiance" />
          <h2 className={cn("font-bold tracking-tight", theme === 'light' ? "text-black" : "text-white")}>Governance Console</h2>
        </div>
        <div className="flex items-center gap-4">
          <div className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl border",
            theme === 'light' ? "bg-green-50 border-green-100 text-green-600" : "bg-green-500/5 border-green-500/10 text-green-400"
          )}>
            <Activity className="w-4 h-4" />
            <span className="text-[10px] font-bold uppercase tracking-widest">System Integrity: Optimal</span>
          </div>
        </div>
      </header>

      <main className="flex-1 p-8 overflow-y-auto custom-scrollbar">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <h3 className={cn("text-4xl font-bold mb-3", theme === 'light' ? "text-black" : "text-white")}>Human-In-The-Loop</h3>
            <p className="text-gray-500 text-base max-w-2xl leading-relaxed">
              Review and authorize high-risk autonomous operations. Barney requires explicit human verification for steps exceeding the safety threshold.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8">
            <section>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 opacity-30" />
                  <h4 className={cn("text-xs font-bold uppercase tracking-widest opacity-40", theme === 'light' ? "text-black" : "text-white")}>
                    Pending Approvals ({pendingSteps.length})
                  </h4>
                </div>
              </div>

              {loading ? (
                <div className="space-y-4">
                  {[1, 2].map(i => (
                    <div key={i} className={cn("h-32 rounded-2xl animate-pulse", theme === 'light' ? "bg-gray-100" : "bg-white/5")} />
                  ))}
                </div>
              ) : pendingSteps.length > 0 ? (
                <PlanVisualizer 
                  steps={pendingSteps} 
                  onApprove={handleApprove} 
                  onReject={handleReject} 
                  theme={theme} 
                />
              ) : (
                <div className={cn(
                  "p-12 rounded-[32px] border border-dashed flex flex-col items-center text-center",
                  theme === 'light' ? "border-gray-200 bg-gray-50" : "border-white/10 bg-white/5"
                )}>
                  <CheckCircle2 className="w-12 h-12 text-green-500/20 mb-4" />
                  <p className="text-sm font-bold uppercase tracking-widest opacity-30">No pending governance actions</p>
                </div>
              )}
            </section>

            <section className="mt-12">
              <div className="flex items-center gap-2 mb-6">
                <History className="w-4 h-4 opacity-30" />
                <h4 className={cn("text-xs font-bold uppercase tracking-widest opacity-40", theme === 'light' ? "text-black" : "text-white")}>
                  Recent Governance Activity
                </h4>
              </div>
              <div className={cn(
                "rounded-[32px] border overflow-hidden",
                theme === 'light' ? "bg-white border-gray-100" : "bg-white/5 border-white/5 backdrop-blur-sm"
              )}>
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className={cn("border-b", theme === 'light' ? "border-gray-100" : "border-white/5")}>
                      <th className="px-6 py-4 font-bold opacity-40 text-[10px] uppercase tracking-widest">Operation</th>
                      <th className="px-6 py-4 font-bold opacity-40 text-[10px] uppercase tracking-widest">Risk</th>
                      <th className="px-6 py-4 font-bold opacity-40 text-[10px] uppercase tracking-widest">Decision</th>
                      <th className="px-6 py-4 font-bold opacity-40 text-[10px] uppercase tracking-widest">Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {[
                      { op: 'Cloud Run Deployment', risk: 45, decision: 'Approved', time: '10m ago' },
                      { op: 'IAM Policy Update', risk: 88, decision: 'Rejected', time: '1h ago' },
                      { op: 'Database Backup', risk: 12, decision: 'Auto-Approved', time: '3h ago' }
                    ].map((row, i) => (
                      <tr key={i} className="hover:bg-white/5 transition-colors">
                        <td className="px-6 py-4 font-medium">{row.op}</td>
                        <td className="px-6 py-4">
                          <span className={cn(
                            "px-2 py-0.5 rounded-full text-[10px] font-bold",
                            row.risk > 70 ? "text-red-500 bg-red-500/10" : row.risk > 30 ? "text-yellow-500 bg-yellow-500/10" : "text-green-500 bg-green-500/10"
                          )}>
                            {row.risk}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={cn(
                            "text-[10px] font-bold uppercase tracking-widest",
                            row.decision === 'Rejected' ? "text-red-500" : "text-green-500"
                          )}>
                            {row.decision}
                          </span>
                        </td>
                        <td className="px-6 py-4 opacity-40 text-xs">{row.time}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
};

import { History } from 'lucide-react';
