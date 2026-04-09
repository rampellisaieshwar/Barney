import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  CheckCircle2, 
  Circle, 
  AlertTriangle, 
  ShieldAlert, 
  ShieldCheck, 
  Play, 
  Pause,
  XCircle,
  Clock,
  ChevronRight
} from 'lucide-react';
import { PlanStep } from '../types';
import { cn } from '../lib/utils';

interface PlanVisualizerProps {
  steps: PlanStep[];
  onApprove: (stepId: string) => void;
  onReject: (stepId: string) => void;
  theme: 'light' | 'dark';
}

export const PlanVisualizer: React.FC<PlanVisualizerProps> = ({ steps, onApprove, onReject, theme }) => {
  const stages = ['explore', 'execute', 'validate'] as const;

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-500 bg-green-500/10 border-green-500/20';
      case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
      case 'critical': return 'text-red-500 bg-red-500/10 border-red-500/20';
      default: return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'running': return <Play className="w-5 h-5 text-azure-radiance animate-pulse" />;
      case 'failed': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'blocked': return <Pause className="w-5 h-5 text-orange-500" />;
      case 'rejected': return <XCircle className="w-5 h-5 text-red-500" />;
      default: return <Circle className="w-5 h-5 opacity-20" />;
    }
  };

  return (
    <div className="space-y-8 py-6">
      {stages.map((stage) => {
        const stageSteps = steps.filter(s => s.stage === stage);
        if (stageSteps.length === 0) return null;

        return (
          <div key={stage} className="space-y-4">
            <div className="flex items-center gap-3 px-2">
              <div className={cn(
                "w-1 h-4 rounded-full",
                stage === 'explore' ? "bg-blue-500" : stage === 'execute' ? "bg-purple-500" : "bg-green-500"
              )} />
              <h3 className={cn(
                "text-[10px] font-bold uppercase tracking-widest opacity-40",
                theme === 'light' ? "text-black" : "text-white"
              )}>
                Stage: {stage}
              </h3>
            </div>

            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {stageSteps.map((step) => (
                  <motion.div
                    key={step.id}
                    layout
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={cn(
                      "group relative rounded-2xl border p-4 transition-all duration-300",
                      theme === 'light' 
                        ? "bg-white border-gray-100 shadow-sm hover:shadow-md" 
                        : "bg-white/5 border-white/5 hover:border-white/10 backdrop-blur-sm"
                    )}
                  >
                    <div className="flex items-start gap-4">
                      <div className="mt-1">{getStatusIcon(step.status)}</div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className={cn(
                            "font-bold text-sm truncate",
                            theme === 'light' ? "text-black" : "text-white"
                          )}>
                            {step.title}
                          </h4>
                          {step.risk && (
                            <div className={cn(
                              "flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[10px] font-bold uppercase tracking-wider",
                              getRiskColor(step.risk.level)
                            )}>
                              <AlertTriangle className="w-3 h-3" />
                              Risk: {step.risk.score}
                            </div>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 leading-relaxed mb-3">
                          {step.description}
                        </p>

                        {/* Governance Controls */}
                        {step.requiresApproval && step.status === 'pending' && (
                          <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={cn(
                              "mt-4 p-4 rounded-xl border flex flex-col gap-3",
                              theme === 'light' ? "bg-orange-50 border-orange-100" : "bg-orange-500/5 border-orange-500/10"
                            )}
                          >
                            <div className="flex items-center gap-2 text-orange-500">
                              <ShieldAlert className="w-4 h-4" />
                              <span className="text-[10px] font-bold uppercase tracking-widest">Governance Checkpoint Required</span>
                            </div>
                            <p className="text-[11px] text-gray-500 italic">
                              "{step.risk?.reasoning}"
                            </p>
                            <div className="flex items-center gap-2">
                              <button 
                                onClick={() => onApprove(step.id)}
                                className="flex-1 bg-azure-radiance text-white py-2 rounded-lg text-[10px] font-bold uppercase tracking-widest flex items-center justify-center gap-2 hover:scale-[1.02] transition-transform"
                              >
                                <ShieldCheck className="w-3.5 h-3.5" /> Approve Step
                              </button>
                              <button 
                                onClick={() => onReject(step.id)}
                                className="px-4 border border-red-500/20 text-red-500 py-2 rounded-lg text-[10px] font-bold uppercase tracking-widest hover:bg-red-500/10 transition-colors"
                              >
                                Reject
                              </button>
                            </div>
                          </motion.div>
                        )}

                        {step.approved && (
                          <div className="mt-2 flex items-center gap-2 text-green-500/60 text-[10px] font-bold uppercase tracking-widest">
                            <ShieldCheck className="w-3.5 h-3.5" /> Human Approved
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>
        );
      })}
    </div>
  );
};
