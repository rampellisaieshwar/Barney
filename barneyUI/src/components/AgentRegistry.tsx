import React from 'react';
import { Search, Plus, Filter, Zap, Shield, Globe, Cpu } from 'lucide-react';
import { motion } from 'motion/react';
import { Agent } from '../types';
import { cn } from '../lib/utils';

const MOCK_AGENTS: Agent[] = [
  {
    id: '1',
    name: 'WebResearcher',
    description: 'Specialized in deep-web scraping and information synthesis.',
    successRate: 98.4,
    toolsUsed: ['Browser', 'Search', 'Scraper'],
    icon: 'Globe'
  },
  {
    id: '2',
    name: 'PythonCoder',
    description: 'Writes, debugs, and executes complex data analysis scripts.',
    successRate: 95.2,
    toolsUsed: ['Python', 'Shell', 'FileSys'],
    icon: 'Cpu'
  },
  {
    id: '3',
    name: 'SecurityAudit',
    description: 'Autonomous vulnerability scanning and penetration testing.',
    successRate: 92.1,
    toolsUsed: ['Nmap', 'Metasploit', 'CustomScripts'],
    icon: 'Shield'
  },
  {
    id: '4',
    name: 'MarketAnalyst',
    description: 'Real-time financial data processing and trend prediction.',
    successRate: 96.8,
    toolsUsed: ['yfinance', 'pandas', 'matplotlib'],
    icon: 'Zap'
  }
];

interface AgentRegistryProps {
  theme: 'light' | 'dark';
}

export const AgentRegistry: React.FC<AgentRegistryProps> = ({ theme }) => {
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
          <Cpu className="w-5 h-5 text-azure-radiance" />
          <h2 className={cn("font-bold tracking-tight", theme === 'light' ? "text-black" : "text-white")}>Agent Registry</h2>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 opacity-30" />
            <input 
              type="text" 
              placeholder="Search agents..." 
              className={cn(
                "rounded-xl pl-10 pr-4 py-2 text-xs outline-none transition-all",
                theme === 'light' ? "bg-gray-100 border border-gray-200 focus:border-azure-radiance" : "bg-white/5 border border-white/10 focus:border-azure-radiance/50"
              )}
            />
          </div>
          <button className="bg-azure-radiance text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 hover:scale-105 transition-transform shadow-lg">
            <Plus className="w-3.5 h-3.5" />
            Build Agent
          </button>
        </div>
      </header>

      <main className="flex-1 p-8 overflow-y-auto custom-scrollbar">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h3 className={cn("text-3xl font-bold mb-2", theme === 'light' ? "text-black" : "text-white")}>Autonomous Library</h3>
              <p className="text-gray-500 text-sm">Manage and deploy specialized intelligence units.</p>
            </div>
            <button className={cn(
              "px-4 py-2 rounded-xl border text-xs font-bold transition-all flex items-center gap-2",
              theme === 'light' ? "bg-white border-gray-200 hover:bg-gray-50" : "bg-white/5 border-white/10 hover:bg-white/10"
            )}>
              <Filter className="w-3.5 h-3.5" />
              Filter
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {MOCK_AGENTS.map((agent, idx) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className={cn(
                  "group relative rounded-[32px] p-8 border transition-all duration-500 hover:scale-[1.02]",
                  theme === 'light' ? "bg-[#F9FAFC] border-gray-100 hover:border-azure-radiance/30 shadow-sm" : "bg-white/5 border-white/5 hover:border-white/20 backdrop-blur-sm shadow-xl"
                )}
              >
                <div className="absolute top-0 right-0 p-6 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Zap className="w-6 h-6 text-azure-radiance" />
                </div>

                <div className="flex items-start gap-5 mb-8">
                  <div className={cn(
                    "w-14 h-14 rounded-2xl flex items-center justify-center border transition-all duration-500",
                    theme === 'light' ? "bg-white border-gray-100 group-hover:border-azure-radiance/20" : "bg-white/5 border-white/10 group-hover:border-white/30"
                  )}>
                    {agent.icon === 'Globe' && <Globe className="w-7 h-7 text-blue-400" />}
                    {agent.icon === 'Cpu' && <Cpu className="w-7 h-7 text-purple-400" />}
                    {agent.icon === 'Shield' && <Shield className="w-7 h-7 text-red-400" />}
                    {agent.icon === 'Zap' && <Zap className="w-7 h-7 text-yellow-400" />}
                  </div>
                  <div>
                    <h4 className={cn("font-bold text-xl mb-1 transition-colors", theme === 'light' ? "text-black group-hover:text-azure-radiance" : "text-white group-hover:text-azure-radiance")}>
                      {agent.name}
                    </h4>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                      <span className="text-[10px] font-bold uppercase tracking-widest opacity-40">Active</span>
                    </div>
                  </div>
                </div>

                <p className="text-gray-500 text-sm leading-relaxed mb-8 h-12 overflow-hidden line-clamp-2">
                  {agent.description}
                </p>

                <div className="space-y-6">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-[10px] font-bold uppercase tracking-widest opacity-30">Success Rate</span>
                      <span className="text-xs font-bold text-azure-radiance">{agent.successRate}%</span>
                    </div>
                    <div className={cn("h-1.5 rounded-full overflow-hidden", theme === 'light' ? "bg-gray-200" : "bg-white/10")}>
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${agent.successRate}%` }}
                        transition={{ duration: 1, delay: 0.5 }}
                        className="h-full bg-gradient-to-r from-azure-radiance to-medium-purple"
                      />
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {agent.toolsUsed.map(tool => (
                      <span key={tool} className={cn(
                        "px-3 py-1.5 rounded-xl text-[9px] font-bold uppercase tracking-wider transition-colors",
                        theme === 'light' ? "bg-white border border-gray-100 text-gray-500" : "bg-white/5 border border-white/5 text-white/40"
                      )}>
                        {tool}
                      </span>
                    ))}
                  </div>
                </div>

                <button className={cn(
                  "w-full mt-8 py-3 rounded-2xl border text-xs font-bold transition-all",
                  theme === 'light' ? "bg-white border-gray-100 text-gray-500 hover:bg-gray-50 hover:text-black" : "bg-white/5 border-white/5 text-white/40 hover:bg-white/10 hover:text-white"
                )}>
                  View Blueprint
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};
