import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  CheckCircle2, 
  Circle, 
  Play, 
  Pause,
  XCircle,
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

export const PlanVisualizer: React.FC<PlanVisualizerProps> = ({ steps, theme }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const stages = ['explore', 'execute', 'validate'] as const;

  const isAnyRunning = steps.some(s => s.status === 'running');
  const isDone = steps.length > 0 && steps.every(s => s.status === 'completed' || s.status === 'failed');

  useEffect(() => {
    if (isAnyRunning) {
      setIsExpanded(true);
    }
    if (isDone) {
      const timer = setTimeout(() => setIsExpanded(false), 800);
      return () => clearTimeout(timer);
    }
  }, [isAnyRunning, isDone]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'running': return <Play className="w-4 h-4 text-azure-radiance animate-pulse" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'blocked': return <Pause className="w-4 h-4 text-orange-500" />;
      default: return <Circle className="w-4 h-4 opacity-20" />;
    }
  };

  return (
    <div className="space-y-2 py-2">
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 px-2 py-1 opacity-40 hover:opacity-100 transition-opacity group"
      >
        <motion.div
          animate={{ rotate: isExpanded ? 90 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronRight className="w-3 h-3" />
        </motion.div>
        <span className={cn(
          "text-[10px] font-bold uppercase tracking-widest",
          theme === 'light' ? "text-black" : "text-white"
        )}>
          {isAnyRunning ? "Thinking..." : "Process Trace"}
        </span>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="space-y-1.5 pl-6">
              {stages.map((stage) => {
                const stageSteps = steps.filter(s => s.stage === stage);
                if (stageSteps.length === 0) return null;

                return (
                  <div key={stage} className="space-y-1.5">
                    {stageSteps.map((step) => (
                      <motion.div
                        key={step.id}
                        layout
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className={cn(
                          "flex items-center gap-3 transition-opacity duration-300",
                          theme === 'light' ? "opacity-60" : "opacity-40"
                        )}
                      >
                        <div className="shrink-0">{getStatusIcon(step.status)}</div>
                        <div className="flex-1 min-w-0">
                          <h4 className={cn(
                            "font-bold text-[10px] uppercase tracking-wider truncate",
                            theme === 'light' ? "text-black" : "text-white"
                          )}>
                            {step.title}
                          </h4>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
