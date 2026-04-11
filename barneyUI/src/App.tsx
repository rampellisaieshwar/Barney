/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from 'react';
import { TaskConsole } from './components/TaskConsole';
import { Settings } from './components/Settings';
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
      "h-screen font-sans selection:bg-azure-radiance/30 transition-colors duration-300",
      theme === 'light' ? "bg-white text-black" : "bg-[#090B1E] text-white"
    )}>
      <main className="h-full w-full overflow-hidden relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentView}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.1 }}
            className="h-full w-full"
          >
            {currentView === 'console' ? (
              <TaskConsole 
                theme={theme} 
                onSettingsClick={() => setCurrentView('settings')}
                onThemeToggle={toggleTheme}
              />
            ) : (
              <Settings 
                theme={theme} 
                onBack={() => setCurrentView('console')} 
              />
            )}
          </motion.div>
        </AnimatePresence>
      </main>

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
