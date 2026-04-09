/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { TaskConsole } from './components/TaskConsole';
import { RightPanel } from './components/RightPanel';
import { UpgradeModal } from './components/UpgradeModal';
import { AgentRegistry } from './components/AgentRegistry';
import { Settings } from './components/Settings';
import { KnowledgeLedger } from './components/KnowledgeLedger';
import { GovernanceConsole } from './components/GovernanceConsole';
import { View } from './types';
import { motion, AnimatePresence } from 'motion/react';
import { Cpu, Loader2 } from 'lucide-react';
import { cn } from './lib/utils';

export default function App() {
  const [currentView, setCurrentView] = useState<View>('console');
  const [isInitializing, setIsInitializing] = useState(true);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [isUpgradeOpen, setIsUpgradeOpen] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsInitializing(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  if (isInitializing) {
    return (
      <div className="h-screen w-screen bg-[#F9FAFC] flex flex-col items-center justify-center gap-6">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="w-20 h-20 bg-black rounded-2xl flex items-center justify-center shadow-2xl"
        >
          <Cpu className="text-white w-10 h-10" />
        </motion.div>
        <div className="flex flex-col items-center gap-2">
          <h1 className="text-black font-bold text-2xl tracking-tighter">Initializing Barney OS</h1>
          <div className="flex items-center gap-2 text-black/40 text-xs font-mono uppercase tracking-widest">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>Loading autonomous neural modules...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn(
      "flex h-screen font-sans selection:bg-azure-radiance/30 transition-colors duration-300",
      theme === 'light' ? "bg-white text-black" : "bg-[#090B1E] text-white"
    )}>
      <Sidebar 
        currentView={currentView} 
        onViewChange={setCurrentView} 
        theme={theme}
        onThemeToggle={toggleTheme}
      />
      
      <div className="flex-1 overflow-hidden relative flex">
        <div className="flex-1 overflow-hidden">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentView}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
              className="h-full w-full"
            >
              {currentView === 'console' && (
                <TaskConsole theme={theme} onUpgradeClick={() => setIsUpgradeOpen(true)} />
              )}
              {currentView === 'governance' && (
                <GovernanceConsole theme={theme} />
              )}
              {currentView === 'registry' && <AgentRegistry theme={theme} />}
              {currentView === 'memory' && <KnowledgeLedger theme={theme} />}
              {currentView === 'settings' && <Settings />}
            </motion.div>
          </AnimatePresence>
        </div>

        {currentView === 'console' && (
          <RightPanel theme={theme} />
        )}
      </div>

      <UpgradeModal 
        isOpen={isUpgradeOpen} 
        onClose={() => setIsUpgradeOpen(false)} 
        theme={theme}
      />

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(0, 0, 0, 0.05);
          border-radius: 10px;
        }
        .dark .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.05);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 0, 0, 0.1);
        }
        .dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.1);
        }
      `}</style>
    </div>
  );
}
