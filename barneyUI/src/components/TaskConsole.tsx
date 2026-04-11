import React, { useState, useRef, useEffect } from 'react';
import { 
  Compass, 
  Zap, 
  Sparkles,
  ArrowUp,
  Cpu,
  Copy,
  RefreshCw,
  Check,
  ChevronRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../lib/utils';
import { PlanStep } from '../types';
import { api } from '../services/api';
import { PlanVisualizer } from './PlanVisualizer';

interface TaskConsoleProps {
  theme: 'light' | 'dark';
  onSettingsClick: () => void;
  onThemeToggle: () => void;
}

export const TaskConsole: React.FC<TaskConsoleProps> = ({ theme, onSettingsClick, onThemeToggle }) => {
  const [goal, setGoal] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string, steps?: PlanStep[] }[]>([]);
  const [currentSteps, setCurrentSteps] = useState<PlanStep[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const [copyFeedback, setCopyFeedback] = useState<number | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, currentSteps]);

  const runProcess = async (userMsg: string) => {
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
        content: finalAnswer || "No answer generated.",
        steps: [...steps]
      }]);
    } catch (error) {
      console.error("Task failure:", error);
    } finally {
      setIsProcessing(false);
      setCurrentSteps([]);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal.trim() || isProcessing) return;

    const userMsg = goal;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setGoal('');
    await runProcess(userMsg);
  };

  const handleRegenerate = async () => {
    if (isProcessing) return;
    
    const lastUserIndex = [...messages].reverse().findIndex(m => m.role === 'user');
    if (lastUserIndex !== -1) {
      const actualIndex = messages.length - 1 - lastUserIndex;
      const lastUserMsg = messages[actualIndex];
      
      // Slice messages to remove old assistant response
      setMessages(prev => prev.slice(0, actualIndex + 1));
      await runProcess(lastUserMsg.content);
    }
  };

  const handleCopy = (text: string, index: number) => {
    // Strip markdown artifacts and extra spacing
    const cleanText = text.replace(/```[\s\S]*?```/g, (m) => m.replace(/```/g, ''))
                          .replace(/[*_#]/g, '')
                          .trim();
    navigator.clipboard.writeText(cleanText);
    setCopyFeedback(index);
    setTimeout(() => setCopyFeedback(null), 2000);
  };

  return (
    <div className={cn(
      "flex-1 flex flex-col h-screen transition-colors duration-300 relative",
      theme === 'light' ? "bg-white" : "bg-[#090B1E]"
    )}>
      {/* Subtle Background Accent */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[300px] bg-azure-radiance/5 blur-[100px] pointer-events-none" />
      
      {/* Minimal Header */}
      <header className="h-20 px-10 flex items-center justify-end z-10">
        <div className="flex items-center gap-6">
          <button 
            onClick={onThemeToggle}
            className="opacity-20 hover:opacity-100 transition-opacity"
          >
            {theme === 'light' ? <Zap className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
          </button>
          <button 
            onClick={onSettingsClick}
            className="opacity-20 hover:opacity-100 transition-opacity"
          >
            <Compass className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Content Area */}
      <main className="flex-1 overflow-y-auto custom-scrollbar px-10 py-4 z-0">
        <div className="max-w-3xl mx-auto h-full flex flex-col">
          <AnimatePresence mode="wait">
            {messages.length === 0 && currentSteps.length === 0 ? (
              <motion.div 
                key="welcome"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex-1 flex flex-col items-center justify-center text-center pb-20"
              >
                <span className={cn(
                  "text-lg opacity-30 font-medium tracking-wide",
                  theme === 'light' ? "text-black" : "text-white"
                )}>
                  Ask anything
                </span>
              </motion.div>
            ) : (
              <motion.div 
                key="chat"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex-1 space-y-12"
              >
            {messages.map((msg, idx) => (
              <motion.div 
                key={idx} 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.2 }}
                className={cn(
                  "flex flex-col gap-2 mb-8 group relative",
                  msg.role === 'user' ? "items-end" : "items-start"
                )}
              >
                <div className={cn(
                  "px-6 py-4 rounded-3xl max-w-[85%] text-base leading-relaxed relative",
                  msg.role === 'user' 
                    ? (theme === 'light' ? "bg-black text-white" : "bg-white text-black")
                    : (theme === 'light' ? "bg-gray-100 text-black" : "bg-white/5 text-white")
                )}>
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  
                  {/* Actions overlay */}
                  {msg.role === 'assistant' && (
                    <div className="absolute -top-10 right-0 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <button 
                        onClick={() => handleCopy(msg.content, idx)}
                        className="p-1.5 rounded-lg hover:bg-gray-500/10 transition-colors text-gray-500"
                        title="Copy Response"
                      >
                        {copyFeedback === idx ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                      <button 
                        onClick={handleRegenerate}
                        className="p-1.5 rounded-lg hover:bg-gray-500/10 transition-colors text-gray-500"
                        title="Regenerate"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>

                {msg.role === 'assistant' && msg.steps && (
                  <div className="w-full mt-2">
                    <PlanVisualizer 
                      steps={msg.steps} 
                      onApprove={() => {}} 
                      onReject={() => {}} 
                      theme={theme} 
                    />
                  </div>
                )}
              </motion.div>
            ))}

            {(currentSteps.length > 0 || isProcessing) && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-start gap-4 mb-8"
              >
                <div className="flex items-center gap-3 px-2">
                  <div className="w-2 h-2 bg-azure-radiance rounded-full animate-pulse" />
                  <span className="text-xs font-bold uppercase tracking-widest opacity-40">Thinking...</span>
                </div>
                {currentSteps.length > 0 && (
                  <div className="w-full opacity-30">
                    <PlanVisualizer 
                      steps={currentSteps} 
                      onApprove={() => {}} 
                      onReject={() => {}} 
                      theme={theme} 
                    />
                  </div>
                )}
              </motion.div>
            )}
            <div ref={scrollRef} className="h-4" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* Focused Input Area */}
      <footer className="p-10 z-10">
        <div className="max-w-3xl mx-auto">
          <motion.form 
            onSubmit={handleSubmit}
            whileTap={{ scale: 0.98 }}
            transition={{ duration: 0.12, ease: "easeOut" }}
            className={cn(
              "relative flex items-center transition-all duration-300 rounded-[32px] border group",
              theme === 'light' 
                ? "bg-white border-gray-100 focus-within:border-azure-radiance" 
                : "bg-white/5 border-white/10 backdrop-blur-xl focus-within:border-azure-radiance/50"
            )}
          >
              ref={inputRef}
              type="text"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="What should Barney do?"
              className="flex-1 bg-transparent px-8 py-6 text-lg outline-none placeholder:opacity-30"
              disabled={isProcessing}
              autoFocus
            />
            <div className="pr-4">
              <button 
                type="submit"
                disabled={!goal.trim() || isProcessing}
                className={cn(
                  "w-12 h-12 rounded-full flex items-center justify-center transition-all",
                  goal.trim() && !isProcessing
                    ? "bg-azure-radiance text-white shadow-lg shadow-azure-radiance/20 scale-100"
                    : "bg-gray-500/10 text-gray-500/30 scale-90"
                )}
              >
                {isProcessing ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <ArrowUp className="w-6 h-6" />
                )}
              </button>
            </div>
          </form>
          <div className="mt-4 flex items-center justify-center gap-4 opacity-20 hover:opacity-40 transition-opacity">
            <span className="text-[10px] font-bold uppercase tracking-widest">Enterprise Secured</span>
            <div className="w-1 h-1 bg-gray-500 rounded-full" />
            <span className="text-[10px] font-bold uppercase tracking-widest">End-to-End Persistence</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
