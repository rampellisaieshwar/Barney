import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Paperclip, 
  Mic, 
  Compass, 
  Zap, 
  PenTool, 
  Image as ImageIcon, 
  UserCircle, 
  Code,
  HelpCircle,
  Gift,
  ChevronDown,
  RotateCcw,
  Copy,
  Share2,
  Sparkles,
  Plus,
  ShieldCheck,
  Activity
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../lib/utils';
import { PlanStep } from '../types';
import { api } from '../services/api';
import { PlanVisualizer } from './PlanVisualizer';

interface TaskConsoleProps {
  theme: 'light' | 'dark';
  onUpgradeClick: () => void;
}

export const TaskConsole: React.FC<TaskConsoleProps> = ({ theme, onUpgradeClick }) => {
  const [goal, setGoal] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string, steps?: PlanStep[] }[]>([]);
  const [currentSteps, setCurrentSteps] = useState<PlanStep[]>([]);
  const [isDevMode, setIsDevMode] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, currentSteps]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal.trim() || isProcessing) return;

    const userMsg = goal;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setGoal('');
    setIsProcessing(true);
    setCurrentSteps([]);

    try {
      const steps: PlanStep[] = [];
      let finalAnswer = "";
      for await (const step of api.streamTask(userMsg)) {
        if (step.title === 'Final Answer') {
          finalAnswer = step.description;
        }
        steps.push(step);
        setCurrentSteps([...steps]);
      }
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: finalAnswer || "I was unable to determine a final answer for this request.",
        steps: [...steps]
      }]);
    } catch (error) {
      console.error("Task execution failed:", error);
    } finally {
      setIsProcessing(false);
      setCurrentSteps([]);
    }
  };

  const handleApprove = (stepId: string) => {
    setCurrentSteps(prev => prev.map(s => 
      s.id === stepId ? { ...s, status: 'completed', approved: true } : s
    ));
    // In a real app, this would call api.approveStep(stepId)
  };

  const handleReject = (stepId: string) => {
    setCurrentSteps(prev => prev.map(s => 
      s.id === stepId ? { ...s, status: 'rejected' } : s
    ));
    // In a real app, this would call api.rejectStep(stepId)
  };

  const quickActions = [
    { title: 'Write copy', icon: PenTool, color: 'bg-[#FF9500]/10 text-[#FF9500]' },
    { title: 'Image generation', icon: ImageIcon, color: 'bg-[#007AFF]/10 text-[#007AFF]' },
    { title: 'Create avatar', icon: UserCircle, color: 'bg-[#34C759]/10 text-[#34C759]' },
    { title: 'Write code', icon: Code, color: 'bg-[#FF2D55]/10 text-[#FF2D55]' },
  ];

  return (
    <div className={cn(
      "flex-1 flex flex-col h-screen transition-colors duration-300 relative",
      theme === 'light' ? "bg-white" : "bg-[#090B1E]"
    )}>
      {/* Background Gradients for Glass Effect */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-azure-radiance/5 blur-[120px] rounded-full pointer-events-none" />
      
      {/* Header */}
      <header className={cn(
        "h-16 px-8 flex items-center justify-between border-b z-10",
        theme === 'light' ? "border-gray-100 bg-white/50 backdrop-blur-md" : "border-white/5 bg-[#090B1E]/50 backdrop-blur-md"
      )}>
        <div className="flex items-center gap-4">
          <h2 className={cn("text-xl font-bold", theme === 'light' ? "text-black" : "text-white")}>Barney Console</h2>
          <div className={cn(
            "flex items-center gap-2 px-3 py-1 rounded-full border text-[9px] font-bold uppercase tracking-widest",
            theme === 'light' ? "bg-green-50 border-green-100 text-green-600" : "bg-green-500/5 border-green-500/10 text-green-400"
          )}>
            <ShieldCheck className="w-3 h-3" />
            Governed Mode Active
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={onUpgradeClick}
            className="bg-[#090B1E] dark:bg-white text-white dark:text-black px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 hover:scale-105 transition-transform shadow-lg"
          >
            <Zap className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
            Upgrade
          </button>
          <button 
            onClick={() => setIsDevMode(!isDevMode)}
            className={cn("px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all border", 
              isDevMode 
                ? "bg-purple-500/10 text-purple-400 border-purple-500/20" 
                : "opacity-40 hover:opacity-100 border-transparent text-gray-500 dark:text-gray-400"
            )}
          >
            <Code className="w-3.5 h-3.5" />
            Dev Mode
          </button>
          <button className="opacity-40 hover:opacity-100 transition-opacity">
            <Gift className="w-5 h-5" />
          </button>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center">
            <div className="w-6 h-6 rounded-full bg-black/20 backdrop-blur-sm border border-white/30" />
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 overflow-y-auto custom-scrollbar p-8 z-0">
        <div className="max-w-3xl mx-auto h-full flex flex-col">
          <AnimatePresence mode="wait">
            {messages.length === 0 && currentSteps.length === 0 ? (
              <motion.div 
                key="welcome"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex-1 flex flex-col items-center justify-center text-center"
              >
                <h1 className={cn("text-6xl font-bold mb-6 tracking-tight", theme === 'light' ? "text-black" : "text-white")}>
                  Welcome to Barney
                </h1>
                <p className="text-gray-500 text-lg mb-12 max-w-lg">
                  Get started by Barney a task and Chat can do the rest. Not sure where to start?
                </p>

                <div className="grid grid-cols-2 gap-4 w-full max-w-2xl">
                  {quickActions.map((action, idx) => (
                    <button 
                      key={idx}
                      className={cn(
                        "p-5 rounded-[24px] border flex items-center justify-between group hover:scale-[1.02] transition-all",
                        theme === 'light' ? "bg-white border-gray-100 shadow-sm" : "bg-white/5 border-white/10 backdrop-blur-sm"
                      )}
                    >
                      <div className="flex items-center gap-4">
                        <div className={cn("w-12 h-12 rounded-2xl flex items-center justify-center", action.color)}>
                          <action.icon className="w-6 h-6" />
                        </div>
                        <span className={cn("font-bold text-base", theme === 'light' ? "text-black" : "text-white")}>
                          {action.title}
                        </span>
                      </div>
                      <div className={cn(
                        "w-8 h-8 rounded-full border flex items-center justify-center opacity-30 group-hover:opacity-100 transition-opacity",
                        theme === 'light' ? "border-gray-200" : "border-white/20"
                      )}>
                        <Plus className="w-4 h-4" />
                      </div>
                    </button>
                  ))}
                </div>
              </motion.div>
            ) : (
              <motion.div 
                key="chat"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex-1 space-y-10"
              >
                {messages.map((msg, idx) => (
                  <div key={idx} className={cn(
                    "flex gap-6",
                    msg.role === 'user' ? "flex-row-reverse" : "flex-row"
                  )}>
                    <div className="flex-shrink-0">
                      {msg.role === 'assistant' ? (
                        <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                           <div className="w-7 h-7 rounded-full bg-black/20 backdrop-blur-sm border border-white/30" />
                        </div>
                      ) : (
                        <img 
                          src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop" 
                          alt="User" 
                          className="w-10 h-10 rounded-full object-cover shadow-md"
                          referrerPolicy="no-referrer"
                        />
                      )}
                    </div>
                    <div className={cn(
                      "max-w-[85%] p-6 rounded-[24px] text-sm leading-relaxed shadow-sm",
                      msg.role === 'user' 
                        ? (theme === 'light' ? "bg-white border border-gray-100 text-black" : "bg-white/10 text-white backdrop-blur-sm")
                        : (theme === 'light' ? "bg-[#F9FAFC] border border-gray-100 text-black" : "bg-white/5 border border-white/5 text-white backdrop-blur-sm")
                    )}>
                      {msg.role === 'assistant' && (
                        <div className="flex items-center gap-2 mb-3 opacity-40 font-bold text-[10px] uppercase tracking-widest">
                          <Sparkles className="w-3.5 h-3.5" />
                          Barney Intelligence v2.0
                        </div>
                      )}
                      <div className="whitespace-pre-wrap text-base font-medium opacity-90">{msg.content}</div>
                      
                      {msg.steps && isDevMode && (
                        <div className="mt-6 border border-purple-500/10 rounded-2xl p-4 bg-purple-500/5">
                          <div className="text-[10px] text-purple-400 font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
                             <ShieldCheck className="w-3 h-3" /> Debug Logs
                          </div>
                          <PlanVisualizer 
                            steps={msg.steps} 
                            onApprove={handleApprove} 
                            onReject={handleReject} 
                            theme={theme} 
                          />
                        </div>
                      )}

                      {msg.role === 'assistant' && (
                        <div className="flex items-center gap-6 mt-6 pt-6 border-t border-gray-100/10">
                          <button className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest opacity-40 hover:opacity-100 transition-opacity">
                            <RotateCcw className="w-3.5 h-3.5" /> Regenerate
                          </button>
                          <button className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest opacity-40 hover:opacity-100 transition-opacity">
                            <Copy className="w-3.5 h-3.5" /> Copy
                          </button>
                          <button className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest opacity-40 hover:opacity-100 transition-opacity">
                            <Share2 className="w-3.5 h-3.5" /> Share
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {currentSteps.length > 0 && (
                  <div className="flex gap-6">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                         <div className="w-7 h-7 rounded-full bg-black/20 backdrop-blur-sm border border-white/30" />
                      </div>
                    </div>
                    <div className={cn(
                      "max-w-[85%] p-6 rounded-[24px] text-sm leading-relaxed shadow-sm w-full",
                      theme === 'light' ? "bg-[#F9FAFC] border border-gray-100 text-black" : "bg-white/5 border border-white/5 text-white backdrop-blur-sm"
                    )}>
                      <div className="flex items-center gap-3 mb-2">
                        <Activity className="w-4 h-4 text-azure-radiance animate-spin" />
                        <span className="text-sm font-semibold opacity-80">Barney is thinking...</span>
                      </div>
                      
                      {isDevMode && (
                        <div className="mt-6 border border-purple-500/10 rounded-2xl p-4 bg-purple-500/5">
                          <div className="text-[10px] text-purple-400 font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
                             <ShieldCheck className="w-3 h-3" /> Live Orchestration
                          </div>
                          <PlanVisualizer 
                            steps={currentSteps} 
                            onApprove={handleApprove} 
                            onReject={handleReject} 
                            theme={theme} 
                          />
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {isProcessing && currentSteps.length === 0 && (
                  <div className="flex gap-6 animate-pulse">
                    <div className="w-10 h-10 rounded-full bg-gray-100" />
                    <div className={cn(
                      "w-32 h-12 rounded-[24px]",
                      theme === 'light' ? "bg-gray-100" : "bg-white/5"
                    )} />
                  </div>
                )}
                <div ref={scrollRef} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* Input Area */}
      <footer className="p-8 z-10">
        <div className="max-w-3xl mx-auto">
          <form 
            onSubmit={handleSubmit}
            className={cn(
              "rounded-[28px] border p-2 transition-all shadow-2xl",
              theme === 'light' ? "bg-white border-gray-200" : "bg-[#090B1E]/80 border-white/10 backdrop-blur-xl"
            )}
          >
            <div className="flex items-center gap-2 px-6 py-3">
              <input
                type="text"
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="Assign a task to Barney..."
                className={cn(
                  "flex-1 bg-transparent border-none outline-none text-base py-2",
                  theme === 'light' ? "text-black placeholder:text-gray-400" : "text-white placeholder:text-white/20"
                )}
              />
              <button 
                type="submit"
                disabled={!goal.trim() || isProcessing}
                className={cn(
                  "p-2.5 rounded-2xl transition-all",
                  goal.trim() ? "text-azure-radiance hover:bg-azure-radiance/10" : "text-gray-300"
                )}
              >
                <Send className="w-6 h-6" />
              </button>
            </div>
            
            <div className={cn(
              "flex items-center justify-between px-6 py-3 border-t mt-2",
              theme === 'light' ? "border-gray-100" : "border-white/5"
            )}>
              <div className="flex items-center gap-6">
                <button className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest opacity-40 hover:opacity-100 transition-opacity">
                  <Paperclip className="w-4 h-4" /> Attach
                </button>
                <button className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest opacity-40 hover:opacity-100 transition-opacity">
                  <Mic className="w-4 h-4" /> Voice Message
                </button>
                <button className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest opacity-40 hover:opacity-100 transition-opacity">
                  <Compass className="w-4 h-4" /> Browse Prompts
                </button>
              </div>
              <span className="text-[10px] font-mono opacity-20">{goal.length} / 3,000</span>
            </div>
          </form>
          <p className="text-center text-[10px] opacity-30 mt-6 font-medium">
            Barney Intelligence v2.0 • Governed Execution • Model: Barney-3-Flash
          </p>
        </div>
      </footer>
    </div>
  );
};
